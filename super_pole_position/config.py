"""Configuration utilities for arcade parity tweaks. 🎛️"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
import os

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover - PyYAML optional
    yaml = None

DEFAULTS = {
    "puddle": {"speed_factor": 0.65, "angle_jitter": 0.2},
    "offroad_factor": 0.5,
    "audio_volume": 0.8,
    "engine_volume": 0.8,
    "voice_volume": 1.0,
    "effects_volume": 0.8,
    "engine_pan_spread": 0.8,
}

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.arcade_parity.yaml"


def load_parity_config() -> dict[str, Any]:
    """Return arcade parity parameters from YAML or defaults."""
    data: dict[str, Any] = {}
    if yaml and CONFIG_PATH.exists():
        try:
            with CONFIG_PATH.open() as fh:
                loaded = yaml.safe_load(fh)
                if isinstance(loaded, dict):
                    data = loaded
        except Exception:
            data = {}
    cfg = DEFAULTS | data
    if "puddle" in data:
        cfg["puddle"] = DEFAULTS["puddle"] | data.get("puddle", {})
    if "audio_volume" in data:
        try:
            cfg["audio_volume"] = float(data["audio_volume"])
        except (TypeError, ValueError):
            cfg["audio_volume"] = DEFAULTS["audio_volume"]
    for key in ("engine_volume", "voice_volume", "effects_volume"):
        if key in data:
            try:
                cfg[key] = float(data[key])
            except (TypeError, ValueError):
                cfg[key] = DEFAULTS[key]
    if "engine_pan_spread" in data:
        try:
            cfg["engine_pan_spread"] = float(data["engine_pan_spread"])
        except (TypeError, ValueError):
            cfg["engine_pan_spread"] = DEFAULTS["engine_pan_spread"]
    if "offroad_factor" in data:
        try:
            cfg["offroad_factor"] = float(data["offroad_factor"])
        except (TypeError, ValueError):
            cfg["offroad_factor"] = DEFAULTS["offroad_factor"]
    return cfg

def load_arcade_parity() -> dict[str, float]:
    """Load arcade parity config from YAML file if present."""

    path = Path(__file__).resolve().parent.parent / "config.arcade_parity.yaml"
    if not path.exists():
        alt = Path(__file__).resolve().parent / "config.arcade_parity.yaml"
        if alt.exists():
            path = alt
    data: dict[str, float] = {}
    if path.exists():
        for line in path.read_text().splitlines():
            if ":" in line:
                key, val = line.split(":", 1)
                try:
                    data[key.strip()] = float(val.strip())
                except ValueError:
                    continue
    return data


def load_config() -> Dict[str, Any]:
    """Return merged configuration from ``config/default.yaml`` and
    ``config/release.yaml`` when in release mode."""

    base = Path(__file__).resolve().parent.parent / "config"
    config: Dict[str, Any] = {}
    if yaml:
        default_file = base / "default.yaml"
        if default_file.exists():
            with default_file.open() as fh:
                data = yaml.safe_load(fh) or {}
                if isinstance(data, dict):
                    config.update(data)
        if os.getenv("ENV") == "production" or os.getenv("RELEASE") == "1":
            release_file = base / "release.yaml"
            if release_file.exists():
                with release_file.open() as fh:
                    data = yaml.safe_load(fh) or {}
                    if isinstance(data, dict):
                        config.update(data)
    return config
