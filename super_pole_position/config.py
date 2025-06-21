from __future__ import annotations

"""Configuration utilities for arcade parity tweaks. 🎛️"""

from pathlib import Path
from typing import Any

try:
    import yaml
except Exception:  # pragma: no cover - PyYAML optional
    yaml = None

DEFAULTS = {
    "puddle": {"speed_factor": 0.65, "angle_jitter": 0.2},
    "audio_volume": 0.8,
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
    return cfg

def load_arcade_parity() -> dict[str, float]:
    """Load arcade parity config from YAML file if present."""

    path = Path(__file__).resolve().parent.parent / "config.arcade_parity.yaml"
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
