#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 MIND INTERFACES, INC. All rights reserved.
# Licensed under the MIT License.

"""
test_audio_triggers.py
Description: Test suite for test_audio_triggers.
"""

import pytest  # noqa: F401

pytest.importorskip("pygame", reason="pygame required for audio tests")

from super_pole_position.envs.pole_position import PolePositionEnv


def test_prepare_voice_on_reset():
    env = PolePositionEnv(render_mode="human")
    env.reset()
    assert env.start_phase == "READY"


def test_step_with_audio_no_exception():
    env = PolePositionEnv(render_mode="human")
    env.reset()
    env.cars[0].speed = 6.0
    env.step((True, False, 1.0))
    env.close()


def test_checkpoint_sound_loaded():
    env = PolePositionEnv(render_mode="human")
    assert env.checkpoint_wave is not None
    env.close()
