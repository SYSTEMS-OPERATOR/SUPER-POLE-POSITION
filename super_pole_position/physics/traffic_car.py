#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 MIND INTERFACES, INC. All rights reserved.
# Licensed under the MIT License.

"""
traffic_car.py
Description: Module for Super Pole Position.
"""


from .car import Car


class TrafficCar(Car):
    """Simple AI car that follows a constant speed profile."""

    def __init__(self, x=0.0, y=0.0, target_speed=5.0):
        super().__init__(x=x, y=y)
        self.target_speed = target_speed
        self.turn_rate = 1.0

    def policy(self, track=None):
        """Return throttle, brake, steer toward the track centerline."""

        throttle = self.speed < self.target_speed
        brake = self.speed > self.target_speed

        steer = 0.0
        if track is not None:
            target_y = track.y_at(self.x)
            offset = target_y - self.y
            steer = max(-1.0, min(1.0, offset * 0.05))

        return throttle, brake, steer
