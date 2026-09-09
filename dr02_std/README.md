# DR02 Std Simulation

This document describes the DR02 Std simulation. After completing the environment
setup in the [DEEPRobotics Simulation README](../README.md), run the following
command from the repository root:

```bash
python3 run_sim.py dr02_std
```

The `drdds` interfaces come from [deep-robotics-msg](https://github.com/DeepRoboticsLab/deep-robotics-msg.git).
Follow [Install the Message Interfaces](../README.md#31-install-the-message-interfaces)
for the shared installer. The simulator and SDK must use the same interface version.

## 1. Configuration

[`config.yaml`](config.yaml) controls the DR02 Std runtime behavior.

| Section | Field | Description |
| --- | --- | --- |
| Root | `scene` | Complete MJCF scene path, relative to `config.yaml`. |
| `simulation` | `timestep_s` | MuJoCo physics timestep in seconds. |
| `simulation` | `publish_frequency_hz` | `/JOINTS_DATA` and IMU publish frequency in Hz. |
| `simulation` | `command_timeout_s` | Command timeout in seconds. Whole mode applies zero torque and continues; upper mode pauses physics and holds the actual pose. |
| `control` | `mode` | `default`, `whole`, or `upper`. |
| `viewer` | `enabled` | Whether to launch the MuJoCo Viewer. |
| `viewer` | `update_frequency_hz` | Viewer refresh frequency in Hz. |
| `viewer` | `distance`, `lookat`, `azimuth`, `elevation` | Free-camera pose. |

## 2. Control Modes

| Mode | Control Scope |
| --- | --- |
| `default` | Equivalent to `whole`. |
| `whole` | `/JOINTS_CMD` controls every MuJoCo actuator. |
| `upper` | `/JOINTS_CMD` controls the waist and arms; the floating base and lower-body joints are constrained by the model. |

After a command timeout, whole mode continues physics with zero torque on every actuator. Upper mode pauses physics and holds the actual pose at the timeout. Upper mode resumes when a new effective control command arrives; all-zero commands do not resume a paused simulation.

## 3. Scene Composition

[`scene.xml`](scene.xml) is the complete MJCF scene selected by the default configuration:

```xml
<include file="model/dr02_std.xml"/>
<include file="../worlds/basic/basic.xml"/>
<include file="../worlds/demo/demo.xml"/>
```

- `model/dr02_std.xml`: DR02 Std simplified-collision MuJoCo model.
- `worlds/basic/basic.xml`: shared skybox, lighting, and collidable ground.
- `worlds/demo/demo.xml`: optional built-in buildings, stairs, terrain, and environment assets.

To run without the demo terrain, remove or comment out only the demo include. The basic environment should remain enabled to keep the ground and lighting. To use a custom world, replace that include with a custom world XML. Include paths are relative to `scene.xml`; place custom world resources under `worlds/` rather than modifying the robot model. To select a different complete scene, change `scene` in `config.yaml`.

Whole mode requires a world with collidable ground. Upper mode can run with the robot model and basic environment only.


## 4. Topics

| Direction | Topic | Type |
| --- | --- | --- |
| SDK to simulator | `/JOINTS_CMD` | `drdds/msg/JointsCmd` |
| Simulator to SDK | `/JOINTS_DATA` | `drdds/msg/Joints` |
| Simulator to SDK | `/IMU_DATA_BASE` | `sensor_msgs/msg/Imu` |

The current simulation publishes the modeled Base IMU data to `/IMU_DATA_BASE` with `base_link` as its frame.

The SDK and MuJoCo model both define 21 joints and actuators. Simulation state is published in the DR02 Std joint order.
