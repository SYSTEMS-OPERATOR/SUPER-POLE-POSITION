#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 MIND INTERFACES, INC. All rights reserved.
# Licensed under the MIT License.

"""
test_crash_animation.py
Description: Test suite for test_crash_animation.
"""

import pytest  # noqa: F401

from super_pole_position.envs.pole_position import PolePositionEnv


def test_crash_animation_trigger():
    env = PolePositionEnv(render_mode="human")
    env.reset()
    # Force crash by positioning traffic on player
    env.traffic[0].x = env.cars[0].x
    env.traffic[0].y = env.cars[0].y
    _, _, _, _, _ = env.step({"throttle": 0, "brake": 0, "steer": 0})
    assert env.crash_timer > 0
