#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 MIND INTERFACES, INC. All rights reserved.
# Licensed under the MIT License.

"""
test_obstacles.py
Description: Test suite for test_obstacles.
"""

import pytest  # noqa: F401
from super_pole_position.physics.track import Track

def test_load_obstacles():
    try:
        track = Track.load_namco("fuji_namco")
    except FileNotFoundError:
        pytest.skip("namco assets missing")
    assert track.obstacles
