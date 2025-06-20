#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 MIND INTERFACES, INC. All rights reserved.
# Licensed under the MIT License.

"""
test_track.py
Description: Test suite for test_track.
"""

import pytest  # noqa: F401

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from super_pole_position.physics.track import Track
from super_pole_position.physics.car import Car


def test_wrap_position():
    track = Track(width=100.0, height=100.0)
    car = Car(x=110.0, y=-5.0)
    track.wrap_position(car)
    assert 0.0 <= car.x < track.width
    assert car.y == -5.0


def test_distance():
    track = Track(width=100.0, height=100.0)
    car1 = Car(x=10.0, y=10.0)
    car2 = Car(x=90.0, y=10.0)
    dist = track.distance(car1, car2)
    # shortest distance across wrap is 20
    assert dist == 20.0


def test_load_named_track():
    track = Track.load("fuji")
    assert track.width > 0
