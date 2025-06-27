#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 MIND INTERFACES, INC. All rights reserved.
# Licensed under the MIT License.

"""
test_gear_shift.py
Description: Test suite for test_gear_shift.
"""

import pytest  # noqa: F401

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from super_pole_position.physics.car import Car
from super_pole_position.envs.pole_position import PolePositionEnv


def test_shift_changes_max_speed():
    car = Car()
    # low gear max ~8
    car.apply_controls(True, False, 0.0, dt=1.0)
    assert car.speed <= car.gear_max[0]
    car.shift(1)
    for _ in range(10):
        car.apply_controls(True, False, 0.0, dt=1.0)
    assert car.speed <= car.gear_max[1]


def test_env_shift_increments_once():
    env = PolePositionEnv(render_mode="human")
    env.reset()
    env.start_timer = 0
    before = env.cars[0].shift_count
    env.step((False, False, 0.0, 1))
    after = env.cars[0].shift_count
    assert after - before == 1
    env.close()


def test_shift_no_increment_at_limit():
    car = Car()
    car.shift(1)
    before = car.shift_count
    car.shift(1)
    assert car.shift_count == before
