#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 MIND INTERFACES, INC. All rights reserved.
# Licensed under the MIT License.

"""
test_env.py
Description: Test suite for test_env.
"""

import pytest  # noqa: F401

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from super_pole_position.envs.pole_position import PolePositionEnv


def test_reset_and_step():
    env = PolePositionEnv(render_mode="human")
    obs, info = env.reset()
    assert env.cars[0].x == 50.0
    assert env.cars[1].x == 150.0

    # Apply a simple action: throttle car0
    obs, reward, done, trunc, info = env.step((True, False, 0.0))
    assert isinstance(reward, float)
    assert len(obs) == 17
    env.close()
