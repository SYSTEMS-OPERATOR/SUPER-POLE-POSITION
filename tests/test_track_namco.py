#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 MIND INTERFACES, INC. All rights reserved.
# Licensed under the MIT License.

"""
test_track_namco.py
Description: Test suite for test_track_namco.
"""


import pytest  # noqa: F401
from super_pole_position.physics.track import Track


def test_load_namco_track():
    try:
        track = Track.load_namco("fuji_namco")
    except FileNotFoundError:
        pytest.skip("namco assets missing")
    assert track.width > 0 and track.height > 0
