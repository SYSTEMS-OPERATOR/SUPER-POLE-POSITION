#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 MIND INTERFACES, INC. All rights reserved.
# Licensed under the MIT License.

"""
test_slipstream_boost.py
Description: Test suite for test_slipstream_boost.
"""

import pytest  # noqa: F401

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from super_pole_position.envs.pole_position import PolePositionEnv


def test_slipstream_boost():
    env = PolePositionEnv(render_mode="human", mode="race")
    env.reset()
    env.start_timer = 0
    lead = env.traffic[0]
    env.cars[0].y = lead.y
    env.cars[0].x = lead.x - 2
    env.cars[0].speed = lead.speed = 5.0
    env.cars[0].gear = 1
    env.step((False, False, 0.0))
    assert env.cars[0].speed > 5.0
    env.close()
