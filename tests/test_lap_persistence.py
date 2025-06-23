#!/usr/bin/env python3
"""Test lap time persistence."""

from pathlib import Path
from super_pole_position.evaluation.lap_times import (
    load_lap_times,
    update_lap_times,
    reset_lap_times,
)


def test_lap_persistence(tmp_path: Path) -> None:
    file = tmp_path / "laps.json"
    reset_lap_times(file)
    update_lap_times(file, "A", 60000)
    update_lap_times(file, "B", 55000)
    laps = load_lap_times(file)
    assert laps[0]["lap_ms"] == 55000
    update_lap_times(file, "C", 52000)
    laps2 = load_lap_times(file)
    assert laps2[0]["lap_ms"] == 52000 and len(laps2) == 3
