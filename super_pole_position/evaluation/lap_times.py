#!/usr/bin/env python3
"""Lap time persistence utilities."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import List, Dict
from urllib import request
import os

logger = logging.getLogger(__name__)
_DEFAULT_FILE = Path(__file__).resolve().parent / "lap_times.json"


def load_lap_times(file: Path | None = None) -> List[Dict]:
    """Return lap time dicts from ``file``."""
    file = file or _DEFAULT_FILE
    if file.exists():
        try:
            data = json.loads(file.read_text())
            return data.get("laps", [])
        except Exception:
            return []
    return []


def update_lap_times(file: Path | None, name: str, lap_ms: int) -> None:
    """Record ``lap_ms`` for ``name`` in ``file``."""
    file = file or _DEFAULT_FILE
    laps = load_lap_times(file)
    laps.append({"name": name, "lap_ms": int(lap_ms)})
    laps = sorted(laps, key=lambda s: s["lap_ms"])[:10]
    try:
        file.write_text(json.dumps({"laps": laps}, indent=2))
    except Exception as exc:  # pragma: no cover - file error
        logger.debug("update_lap_times error: %s", exc)


def reset_lap_times(file: Path | None = None) -> None:
    """Clear all lap times in ``file``."""
    file = file or _DEFAULT_FILE
    try:
        file.write_text(json.dumps({"laps": []}, indent=2))
    except Exception as exc:  # pragma: no cover - file error
        logger.debug("reset_lap_times error: %s", exc)


def submit_lap_time_http(
    name: str, lap_ms: int, host: str = "127.0.0.1", port: int = 8000
) -> bool:
    """POST ``lap_ms`` for ``name`` to the scoreboard server."""
    if os.getenv("ALLOW_NET") != "1":
        return False
    url = f"http://{host}:{port}/laps"
    data = json.dumps({"name": name, "lap_ms": int(lap_ms)}).encode()
    req = request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with request.urlopen(req, timeout=1) as resp:  # pragma: no cover - network
            return 200 <= resp.status < 300
    except Exception:  # pragma: no cover - network failure
        return False
