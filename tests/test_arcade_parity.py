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

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from super_pole_position.physics.car import Car
from super_pole_position.physics.track import Track, Puddle




def measure_puddle_ratio() -> float:
    """Return slowdown ratio when a car drives through a puddle."""

    track = Track(width=200.0, height=200.0, puddles=[Puddle(x=50, y=50, radius=10)])
    car = Car(x=50, y=50)
    car.apply_controls(throttle=1.0, brake=0.0, steering=0.0, track=track, dt=1.0)
    pre = car.speed
    car.apply_controls(throttle=0.0, brake=0.0, steering=0.0, track=track, dt=1.0)
    post = car.speed
    return post / pre


def test_puddle_slowdown_improved():
    with open("benchmarks/baseline_puddle.txt") as fh:
        baseline_ratio = float(fh.read().split()[1])
    ratio = measure_puddle_ratio()
    assert ratio < baseline_ratio - 0.04

def test_engine_pitch_improved():
    baseline_path = Path('benchmarks/baseline_engine_pitch.txt')
    baseline_val = float(baseline_path.read_text().split('=')[1])
    new_val = engine_pitch(0.5, 0)
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
