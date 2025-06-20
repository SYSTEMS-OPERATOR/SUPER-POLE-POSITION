#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 MIND INTERFACES, INC. All rights reserved.
# Licensed under the MIT License.

"""
test_offroad_speed.py
Description: Test suite for test_offroad_speed.
"""

import pytest  # noqa: F401

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from super_pole_position.envs.pole_position import PolePositionEnv


def test_offroad_speed():
    env = PolePositionEnv(render_mode="human", mode="race")
    env.reset()
    env.start_timer = 0
    env.cars[0].y = 1.0  # near edge -> off-road
    env.cars[0].gear = 1
    env.step((True, False, 0.0))
    assert env.cars[0].speed < env.cars[0].acceleration
    env.close()
