#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 MIND INTERFACES, INC. All rights reserved.
# Licensed under the MIT License.

"""
test_audio_triggers.py
Description: Test suite for test_audio_triggers.
"""

import pytest  # noqa: F401

from super_pole_position.envs.pole_position import PolePositionEnv


def test_prepare_voice_on_reset():
    env = PolePositionEnv(render_mode="human")
    env.reset()
    assert env.start_phase == "READY"
