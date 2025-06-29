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
import random


def test_seed_passthrough() -> None:
    env = PolePositionEnv(render_mode="human")
    env.reset(seed=42)
    first = random.random()
    env.reset(seed=42)
    second = random.random()
    env.close()
    assert first == second


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


def test_custom_parameters() -> None:
    """Initialize ``PolePositionEnv`` with non-default settings."""
    env = PolePositionEnv(
        render_mode="human",
        mode="qualify",
        track_name="fuji",
        hyper=True,
        player_name="ACE",
        slipstream=False,
    )
    env.reset()
    assert env.mode == "qualify"
    assert env.player_name == "ACE"
    assert env.slipstream_enabled is False
    assert env.hyper is True
    env.close()
