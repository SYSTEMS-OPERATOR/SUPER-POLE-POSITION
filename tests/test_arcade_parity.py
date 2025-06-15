#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_arcade_parity.py
Description: Benchmark scanline effect intensity.
"""

from pathlib import Path

import pytest  # noqa: F401

from super_pole_position.ui import arcade
from super_pole_position.envs.pole_position import engine_pitch
from pathlib import Path

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from super_pole_position.envs.pole_position import PolePositionEnv
from super_pole_position.physics.track import Track, Puddle

import pathlib

from super_pole_position.ui.arcade import SCANLINE_ALPHA


def test_scanline_intensity_improved():
    baseline_path = pathlib.Path(__file__).with_name("baseline_scanline.txt")
    baseline_alpha = int(baseline_path.read_text().strip())
    assert SCANLINE_ALPHA >= baseline_alpha + 5

def measure_puddle_ratio() -> float:
    env = PolePositionEnv(render_mode="human")
    env.track = Track(width=200.0, height=200.0, puddles=[Puddle(x=50, y=50, radius=10)])
    env.reset()
    env.step({"throttle": True, "brake": False, "steer": 0.0})
    pre = env.cars[0].speed
    env.step({"throttle": False, "brake": False, "steer": 0.0})
    post = env.cars[0].speed
    return post / pre


def test_puddle_slowdown_improved():
    with open("benchmarks/baseline_puddle.txt") as fh:
        baseline_ratio = float(fh.read().split()[1])
    ratio = measure_puddle_ratio()
    assert ratio < baseline_ratio - 0.04

def test_engine_pitch_improved():
    baseline_path = Path('benchmarks/baseline_engine_pitch.txt')
    baseline_val = float(baseline_path.read_text().split('=')[1])
    new_val = engine_pitch(0.5)
    assert new_val - baseline_val >= 49.9

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
