"""DR02 Pro MuJoCo simulation and ROS 2 Topic bridge."""

from __future__ import annotations

from pathlib import Path
import signal
import time

import mujoco
import numpy as np
import rclpy
from drdds.msg import JointValue, Joints, JointsCmd, MetaType
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
from rclpy.signals import SignalHandlerOptions
from sensor_msgs.msg import Imu

from sim_config import SimulationConfig, load_config
from simulator import MuJoCoSimulator


DOF_NUM = 31
UPPER_BODY_DOF_NUM = 17
MUJOCO_ACTUATOR_NUM = 29
COMMAND_QOS_QUEUE_DEPTH = 50
STARTUP_KEYFRAME = "default"

ACTUATOR_JOINT_NAMES = (
    "waist_z_joint", "waist_x_joint", "waist_y_joint",
    "left_shoulder_y_joint", "left_shoulder_x_joint", "left_shoulder_z_joint",
    "left_elbow_joint", "left_wrist_z_joint", "left_wrist_y_joint", "left_wrist_x_joint",
    "right_shoulder_y_joint", "right_shoulder_x_joint", "right_shoulder_z_joint",
    "right_elbow_joint", "right_wrist_z_joint", "right_wrist_y_joint", "right_wrist_x_joint",
    "left_hip_y_joint", "left_hip_x_joint", "left_hip_z_joint", "left_knee_joint",
    "left_ankle_y_joint", "left_ankle_x_joint",
    "right_hip_y_joint", "right_hip_x_joint", "right_hip_z_joint", "right_knee_joint",
    "right_ankle_y_joint", "right_ankle_x_joint",
)

UPPER_CONSTRAINT_NAMES = (
    "upper_base_lock",
    "upper_left_hip_y_lock", "upper_left_hip_x_lock", "upper_left_hip_z_lock",
    "upper_left_knee_lock", "upper_left_ankle_y_lock", "upper_left_ankle_x_lock",
    "upper_right_hip_y_lock", "upper_right_hip_x_lock", "upper_right_hip_z_lock",
    "upper_right_knee_lock", "upper_right_ankle_y_lock", "upper_right_ankle_x_lock",
)


def resolve_control_mode(mode: str) -> str:
    """Resolve DR02 Pro's default mode without imposing it on other products."""
    if mode == "default":
        return "whole"
    if mode in ("whole", "upper"):
        return mode
    raise ValueError(f"Unsupported DR02 Pro control.mode: {mode}")


class DR2ProSimulation(Node):
    """Bridge DR02 Pro joint Topics to the canonical MuJoCo model."""

    def __init__(self, config: SimulationConfig) -> None:
        super().__init__("dr02_pro_simulation")
        self.config = config
        self.control_mode = resolve_control_mode(config.control_mode)
        self.simulator = MuJoCoSimulator(config.scene_path, config)
        self.model = self.simulator.model
        self.data = self.simulator.data
        self.mujoco_actuator_num = int(self.model.nu)

        self._validate_model()
        self.simulator.reset_to_keyframe(STARTUP_KEYFRAME)
        self._set_upper_constraints(self.control_mode == "upper")

        self.joint_pos = np.zeros(DOF_NUM, dtype=np.float64)
        self.joint_vel = np.zeros(DOF_NUM, dtype=np.float64)
        self.joint_tau = np.zeros(DOF_NUM, dtype=np.float64)
        self.goal_joint_pos = np.zeros(MUJOCO_ACTUATOR_NUM, dtype=np.float64)
        self.goal_joint_vel = np.zeros(MUJOCO_ACTUATOR_NUM, dtype=np.float64)
        self.kp = np.zeros(MUJOCO_ACTUATOR_NUM, dtype=np.float64)
        self.kd = np.zeros(MUJOCO_ACTUATOR_NUM, dtype=np.float64)
        self.tau_ff = np.zeros(MUJOCO_ACTUATOR_NUM, dtype=np.float64)
        self._joint_qpos_adrs, self._joint_dof_adrs = self._joint_addresses()
        self._received_command = False
        self._last_command_time: float | None = None
        self._paused_for_timeout = False
        self._frame_id = 0
        self._stop_requested = False

        state_qos = QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
            reliability=ReliabilityPolicy.BEST_EFFORT,
        )
        self.joint_pub = self.create_publisher(Joints, "/JOINTS_DATA", state_qos)
        self.imu_head_pub = self.create_publisher(
            Imu, "/IMU_DATA_HEAD", state_qos
        )
        self.imu_base_pub = self.create_publisher(
            Imu, "/IMU_DATA_BASE", state_qos
        )
        self.cmd_sub = self.create_subscription(
            JointsCmd,
            "/JOINTS_CMD",
            self._handle_joint_command,
            COMMAND_QOS_QUEUE_DEPTH,
        )
        self._publish_timer = self.create_timer(
            1.0 / self.config.publish_frequency_hz, self._publish_state
        )

        self.get_logger().info(
            f"DR02 Pro simulation ready in {self.control_mode} mode: "
            "/JOINTS_CMD -> /JOINTS_DATA, /IMU_DATA_HEAD, /IMU_DATA_BASE"
        )

    def _validate_model(self) -> None:
        if self.mujoco_actuator_num != MUJOCO_ACTUATOR_NUM:
            raise RuntimeError(
                f"Expected {MUJOCO_ACTUATOR_NUM} MuJoCo actuators, "
                f"got {self.mujoco_actuator_num}"
            )

        for index, joint_name in enumerate(ACTUATOR_JOINT_NAMES):
            joint_id = mujoco.mj_name2id(
                self.model, mujoco.mjtObj.mjOBJ_JOINT, joint_name
            )
            actuator_id = mujoco.mj_name2id(
                self.model, mujoco.mjtObj.mjOBJ_ACTUATOR, joint_name
            )
            if joint_id < 0 or actuator_id != index:
                raise RuntimeError(f"Invalid actuator mapping for {joint_name}")
            if self.model.actuator_trnid[actuator_id, 0] != joint_id:
                raise RuntimeError(f"Actuator {joint_name} does not target its joint")

        for constraint_name in UPPER_CONSTRAINT_NAMES:
            if mujoco.mj_name2id(
                self.model, mujoco.mjtObj.mjOBJ_EQUALITY, constraint_name
            ) < 0:
                raise RuntimeError(f"Missing upper-mode constraint: {constraint_name}")

        for sensor_name in ("base_quat", "base_acc", "base_omega"):
            if mujoco.mj_name2id(
                self.model, mujoco.mjtObj.mjOBJ_SENSOR, sensor_name
            ) < 0:
                raise RuntimeError(f"Missing IMU sensor: {sensor_name}")

    def _joint_addresses(self) -> tuple[np.ndarray, np.ndarray]:
        qpos_adrs = np.empty(MUJOCO_ACTUATOR_NUM, dtype=np.int32)
        dof_adrs = np.empty(MUJOCO_ACTUATOR_NUM, dtype=np.int32)
        for index, joint_name in enumerate(ACTUATOR_JOINT_NAMES):
            joint_id = mujoco.mj_name2id(
                self.model, mujoco.mjtObj.mjOBJ_JOINT, joint_name
            )
            qpos_adrs[index] = self.model.jnt_qposadr[joint_id]
            dof_adrs[index] = self.model.jnt_dofadr[joint_id]
        return qpos_adrs, dof_adrs

    def _set_upper_constraints(self, enabled: bool) -> None:
        for constraint_name in UPPER_CONSTRAINT_NAMES:
            constraint_id = mujoco.mj_name2id(
                self.model, mujoco.mjtObj.mjOBJ_EQUALITY, constraint_name
            )
            self.data.eq_active[constraint_id] = enabled
        mujoco.mj_forward(self.model, self.data)

    def _handle_joint_command(self, msg: JointsCmd) -> None:
        if len(msg.data) != DOF_NUM:
            self.get_logger().warning(
                f"Ignoring /JOINTS_CMD with {len(msg.data)} joints; expected {DOF_NUM}"
            )
            return

        active_actuator_num = (
            UPPER_BODY_DOF_NUM
            if self.control_mode == "upper"
            else MUJOCO_ACTUATOR_NUM
        )
        has_active_control = any(
            msg.data[index].kp != 0.0
            or msg.data[index].kd != 0.0
            or msg.data[index].torque != 0.0
            for index in range(active_actuator_num)
        )
        if (
            not self._received_command or self._paused_for_timeout
        ) and not has_active_control:
            return

        for index in range(MUJOCO_ACTUATOR_NUM):
            if self.control_mode == "upper" and index >= UPPER_BODY_DOF_NUM:
                continue
            command = msg.data[index]
            self.goal_joint_pos[index] = command.position
            self.goal_joint_vel[index] = command.velocity
            self.kp[index] = command.kp
            self.kd[index] = command.kd
            self.tau_ff[index] = command.torque

        self._received_command = True
        self._last_command_time = time.perf_counter()
        self._paused_for_timeout = False

    def _apply_joint_command(self) -> bool:
        if (
            self._last_command_time is None
            or time.perf_counter() - self._last_command_time > self.config.command_timeout_s
        ):
            self.data.ctrl.fill(0.0)
            self.joint_tau.fill(0.0)
            if self.control_mode == "upper":
                if not self._paused_for_timeout:
                    self.data.qvel.fill(0.0)
                    mujoco.mj_forward(self.model, self.data)
                    self._paused_for_timeout = True
                return False
            return True

        position_error = self.goal_joint_pos - self.data.qpos[self._joint_qpos_adrs]
        velocity_error = self.goal_joint_vel - self.data.qvel[self._joint_dof_adrs]
        self.joint_tau[:MUJOCO_ACTUATOR_NUM] = (
            self.kp * position_error + self.kd * velocity_error + self.tau_ff
        )
        self.joint_tau[MUJOCO_ACTUATOR_NUM:] = 0.0
        self.data.ctrl[:] = self.joint_tau[:MUJOCO_ACTUATOR_NUM]
        return True

    def _sensor_data(self, sensor_name: str) -> np.ndarray:
        sensor_id = mujoco.mj_name2id(
            self.model, mujoco.mjtObj.mjOBJ_SENSOR, sensor_name
        )
        address = self.model.sensor_adr[sensor_id]
        dimension = self.model.sensor_dim[sensor_id]
        return self.data.sensordata[address:address + dimension]

    def _header(self) -> MetaType:
        header = MetaType()
        header.frame_id = self._frame_id
        header.stamp = self.get_clock().now().to_msg()
        return header

    def _publish_state(self) -> None:
        self.joint_pos[:MUJOCO_ACTUATOR_NUM] = self.data.qpos[self._joint_qpos_adrs]
        self.joint_vel[:MUJOCO_ACTUATOR_NUM] = self.data.qvel[self._joint_dof_adrs]
        self.joint_pos[MUJOCO_ACTUATOR_NUM:] = 0.0
        self.joint_vel[MUJOCO_ACTUATOR_NUM:] = 0.0

        base_quat = self._sensor_data("base_quat")
        base_acc = self._sensor_data("base_acc")
        base_omega = self._sensor_data("base_omega")
        header = self._header()

        imu = Imu()
        imu.header.stamp = header.stamp
        imu.header.frame_id = "base_link"
        imu.orientation.x = float(base_quat[1])
        imu.orientation.y = float(base_quat[2])
        imu.orientation.z = float(base_quat[3])
        imu.orientation.w = float(base_quat[0])
        imu.angular_velocity.x, imu.angular_velocity.y, imu.angular_velocity.z = map(
            float, base_omega
        )
        imu.linear_acceleration.x, imu.linear_acceleration.y, imu.linear_acceleration.z = map(
            float, base_acc
        )
        self.imu_head_pub.publish(imu)
        self.imu_base_pub.publish(imu)

        joints = Joints()
        joints.header = header
        joints.data = [JointValue() for _ in range(DOF_NUM)]
        for index, joint in enumerate(joints.data):
            joint.name = [32, 32, 32, 32]
            joint.data_id = 0
            joint.status_word = 1
            joint.position = float(self.joint_pos[index])
            joint.velocity = float(self.joint_vel[index])
            joint.torque = float(self.joint_tau[index])
            joint.motion_temp = 40.0
            joint.driver_temp = 45.0
        self.joint_pub.publish(joints)
        self._frame_id += 1

    def request_stop(self) -> None:
        self._stop_requested = True

    def run(self) -> None:
        try:
            while rclpy.ok() and not self._stop_requested:
                rclpy.spin_once(self, timeout_sec=0.0)

                if not self._received_command:
                    if not self.simulator.sync_viewer():
                        break
                    time.sleep(self.config.timestep_s)
                    continue

                if not self._apply_joint_command():
                    if not self.simulator.sync_viewer():
                        break
                    time.sleep(self.config.timestep_s)
                    continue

                self.simulator.step()
                if not self.simulator.sync_viewer():
                    break
        finally:
            self.simulator.close()


def run(config_path: str | Path) -> int:
    """Run DR02 Pro simulation from the repository entry point."""
    rclpy.init(signal_handler_options=SignalHandlerOptions.NO)
    simulation = None
    previous_signal_handlers = {}
    try:
        simulation = DR2ProSimulation(load_config(config_path))

        def handle_signal(_signum, _frame) -> None:
            simulation.request_stop()

        for signum in (signal.SIGINT, signal.SIGTERM):
            previous_signal_handlers[signum] = signal.getsignal(signum)
            signal.signal(signum, handle_signal)

        simulation.run()
        return 0
    except KeyboardInterrupt:
        return 0
    finally:
        if simulation is not None:
            simulation.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
        for signum, handler in previous_signal_handlers.items():
            signal.signal(signum, handler)
