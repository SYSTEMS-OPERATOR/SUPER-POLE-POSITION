#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 MIND INTERFACES, INC. All rights reserved.
# Licensed under the MIT License.

"""
test_timer_checkpoint.py
Description: Test suite for test_timer_checkpoint.
"""

import pytest  # noqa: F401

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from super_pole_position.envs.pole_position import PolePositionEnv


def test_checkpoint_timer_rollover():
    env = PolePositionEnv(render_mode="human", mode="race")
    env.reset()
    env.start_timer = 0
    env.cars[0].gear = 1
    before = env.remaining_time
    env.cars[0].x = env.track.start_x - 1
    env.step((False, False, 0.0))
    env.cars[0].x = env.track.start_x + 1
    env.step((False, False, 0.0))
    assert env.remaining_time > before
    env.close()
