"""Generic MuJoCo lifecycle and real-time stepping support."""

import time
from pathlib import Path

import mujoco
import mujoco.viewer

from sim_config import SimulationConfig


class MuJoCoSimulator:
    """Owns a MuJoCo model, data, optional viewer, and fixed-rate stepping."""

    def __init__(self, scene_path: Path, config: SimulationConfig) -> None:
        self.model = mujoco.MjModel.from_xml_path(str(scene_path))
        self.model.opt.timestep = config.timestep_s
        self.data = mujoco.MjData(self.model)
        self._timestep_s = config.timestep_s
        self._next_step_time: float | None = None
        self._step_count = 0
        self._render_interval = max(
            1, round(1.0 / (config.timestep_s * config.viewer.update_frequency_hz))
        )
        self._viewer = None

        if config.viewer.enabled:
            self._viewer = mujoco.viewer.launch_passive(self.model, self.data)
            self._viewer.cam.distance = config.viewer.distance
            self._viewer.cam.lookat = config.viewer.lookat
            self._viewer.cam.azimuth = config.viewer.azimuth
            self._viewer.cam.elevation = config.viewer.elevation

    def reset_to_keyframe(self, keyframe_name: str) -> None:
        keyframe_id = mujoco.mj_name2id(
            self.model, mujoco.mjtObj.mjOBJ_KEY, keyframe_name
        )
        if keyframe_id < 0:
            raise ValueError(f"Unknown MuJoCo keyframe: {keyframe_name}")
        mujoco.mj_resetDataKeyframe(self.model, self.data, keyframe_id)
        mujoco.mj_forward(self.model, self.data)

    def step(self) -> None:
        now = time.perf_counter()
        if self._next_step_time is None:
            self._next_step_time = now
        if now < self._next_step_time:
            time.sleep(self._next_step_time - now)

        mujoco.mj_step(self.model, self.data)
        self._step_count += 1
        self._next_step_time += self._timestep_s

        now = time.perf_counter()
        if self._next_step_time < now - self._timestep_s:
            self._next_step_time = now

    def sync_viewer(self) -> bool:
        if self._viewer is None or self._step_count % self._render_interval:
            return True
        if not self._viewer.is_running():
            return False
        self._viewer.sync()
        return True

    def close(self) -> None:
        if self._viewer is not None:
            viewer = self._viewer
            self._viewer = None
            viewer.close()
            # close() only requests exit; wait for the render thread to release GL.
            while viewer._sim() is not None:
                time.sleep(0.001)
