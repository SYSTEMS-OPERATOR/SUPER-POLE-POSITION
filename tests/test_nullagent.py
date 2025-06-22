#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 MIND INTERFACES, INC. All rights reserved.
# Licensed under the MIT License.

"""
test_nullagent.py
Description: Test suite for test_nullagent.
"""

import pytest  # noqa: F401

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from super_pole_position.envs.pole_position import PolePositionEnv
from super_pole_position.agents.base_llm_agent import NullAgent


def test_null_agent_completes_lap():
    env = PolePositionEnv(render_mode="human", mode="race")
    env.reset()
    env.start_timer = 0
    agent = NullAgent()
    steps = 0
    while env.lap < 1 and steps < 400:
        obs = env._get_obs()
        action = agent.act(obs)
        env.step(action)
        steps += 1
    assert env.lap >= 1
    env.close()
