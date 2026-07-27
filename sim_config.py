"""Configuration loading shared by simulation products."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


REPOSITORY_ROOT = Path(__file__).resolve().parent


@dataclass(frozen=True)
class ViewerConfig:
    enabled: bool
    update_frequency_hz: float
    distance: float
    lookat: tuple[float, float, float]
    azimuth: float
    elevation: float


@dataclass(frozen=True)
class SimulationConfig:
    scene_path: Path
    timestep_s: float
    publish_frequency_hz: float
    command_timeout_s: float
    control_mode: str
    viewer: ViewerConfig


def _mapping(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be a mapping")
    return value


def _positive(value: Any, name: str) -> float:
    result = float(value)
    if result <= 0.0:
        raise ValueError(f"{name} must be greater than zero")
    return result


def load_config(config_path: str | Path) -> SimulationConfig:
    """Load the runtime settings and MJCF scene from a product configuration."""
    path = Path(config_path)
    if not path.is_absolute():
        path = REPOSITORY_ROOT / path
    path = path.resolve()

    with path.open(encoding="utf-8") as config_file:
        raw = _mapping(yaml.safe_load(config_file), "config")

    simulation = _mapping(raw.get("simulation"), "simulation")
    viewer_raw = _mapping(raw.get("viewer"), "viewer")
    control = _mapping(raw.get("control"), "control")

    scene_path = Path(str(raw["scene"]))
    if not scene_path.is_absolute():
        scene_path = path.parent / scene_path
    scene_path = scene_path.resolve()
    if not scene_path.is_file():
        raise FileNotFoundError(f"Scene file not found: {scene_path}")

    lookat = tuple(float(value) for value in viewer_raw["lookat"])
    if len(lookat) != 3:
        raise ValueError("viewer.lookat must contain three values")

    return SimulationConfig(
        scene_path=scene_path,
        timestep_s=_positive(simulation["timestep_s"], "simulation.timestep_s"),
        publish_frequency_hz=_positive(
            simulation["publish_frequency_hz"], "simulation.publish_frequency_hz"
        ),
        command_timeout_s=_positive(
            simulation["command_timeout_s"], "simulation.command_timeout_s"
        ),
        control_mode=str(control["mode"]),
        viewer=ViewerConfig(
            enabled=bool(viewer_raw["enabled"]),
            update_frequency_hz=_positive(
                viewer_raw["update_frequency_hz"], "viewer.update_frequency_hz"
            ),
            distance=_positive(viewer_raw["distance"], "viewer.distance"),
            lookat=lookat,
            azimuth=float(viewer_raw["azimuth"]),
            elevation=float(viewer_raw["elevation"]),
        ),
    )
