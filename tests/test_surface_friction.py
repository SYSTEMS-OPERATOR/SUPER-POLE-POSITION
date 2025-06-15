#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_surface_friction.py
Description: Test surface friction slows car.
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from super_pole_position.physics.car import Car
from super_pole_position.physics.track import Track, SurfaceZone


def test_surface_zone_friction():
    zone = SurfaceZone(x=0, y=0, width=10, height=10, friction=0.5)
    track = Track(width=50, height=50, surfaces=[zone])
    car = Car()
    car.x = 5
    car.y = 5
    car.apply_controls(True, False, 0.0, dt=1.0, track=track)
    assert car.speed < car.acceleration
