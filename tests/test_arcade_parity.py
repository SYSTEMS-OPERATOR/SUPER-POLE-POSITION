#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_arcade_parity.py
Description: Benchmark scanline effect intensity.
"""

from pathlib import Path

import pytest  # noqa: F401

from super_pole_position.ui import arcade


def _read_baseline() -> int:
    base = Path(__file__).resolve().parent / "baseline.txt"
    for line in base.read_text().splitlines():
        if "scanline_alpha" in line:
            return int(line.split(":", 1)[1].strip())
    return 255


def test_scanline_intensity_improved():
    baseline = _read_baseline()
    cfg = arcade._load_arcade_config()
    assert cfg["scanline_alpha"] <= baseline - 10

