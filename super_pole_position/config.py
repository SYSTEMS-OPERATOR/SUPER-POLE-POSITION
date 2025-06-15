from __future__ import annotations

import os
from pathlib import Path


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
