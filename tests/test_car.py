#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 MIND INTERFACES, INC. All rights reserved.
# Licensed under the MIT License.

"""
test_car.py
Description: Test suite for test_car.
"""

import pytest  # noqa: F401

import math
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from super_pole_position.physics.car import Car

def test_apply_controls_throttle_brake():
    car = Car()
    car.apply_controls(throttle=True, brake=False, steering=0.0, dt=1.0)
    assert math.isclose(car.speed, car.acceleration)

    car.apply_controls(throttle=False, brake=True, steering=0.0, dt=1.0)
    assert car.speed == 0.0
