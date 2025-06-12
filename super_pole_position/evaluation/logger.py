"""Utility for writing simple JSON benchmark logs."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from .metrics import summary


def log_episode(env, file: Path | None = None) -> Path:
    """Write a JSON summary for ``env`` to ``file``.

    :param env: Environment with metrics attributes.
    :param file: Optional explicit path. Defaults to ``benchmarks/YYYY-MM-DD/<timestamp>.json``.
    :return: Path to the file written.
    """
    date_dir = Path("benchmarks") / datetime.utcnow().strftime("%Y-%m-%d")
    date_dir.mkdir(parents=True, exist_ok=True)
    if file is None:
        timestamp = datetime.utcnow().strftime("%H%M%S")
        file = date_dir / f"{timestamp}.json"

    data = summary(env)
    data["timestamp"] = datetime.utcnow().isoformat()
    file.write_text(json.dumps(data, indent=2))
    return file
