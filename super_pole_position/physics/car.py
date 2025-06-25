#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 MIND INTERFACES, INC. All rights reserved.
# Licensed under the MIT License.

"""
car.py
Description: Module for Super Pole Position.
"""



import math

from ..config import load_arcade_parity

_ARC_CFG = load_arcade_parity()

class Car:
    """A basic arcade-style car with position, speed, angle, acceleration."""
    length = 2.0
    width = 1.0

    def __init__(
        self,
        x: float = 0.0,
        y: float = 0.0,
        angle: float = 0.0,
        speed: float = 0.0,
        turn_rate: float | None = None,
    ) -> None:
        self.x = x
        self.y = y
        self.angle = angle  # Radians; 0 means facing 'east' by convention
        self.speed = speed
        self.acceleration = 2.0
        # Two gear ratios: index 0=LOW, 1=HIGH
        # Low gear revised to ~120 MPH for arcade parity
        self.gear_max = [54.0, 85.0]
        self.gear = 0
        self.max_speed = self.gear_max[-1]
        # Slightly quicker steering for responsive handling
        default_turn = float(_ARC_CFG.get("turn_rate", 2.5))
        self.turn_rate = turn_rate if turn_rate is not None else default_turn
        self.shift_count = 0
        # If True speed is not clamped by gear ratios (Hyper mode)
        self.unlimited = False

    def rpm(self) -> float:
        """Return 0..1 engine RPM based on current gear limit."""

        return min(1.0, self.speed / self.gear_max[self.gear])

    def shift(self, change: int) -> bool:
        """Change gear by ``change`` amount and return ``True`` if shifted."""
        if change:
            self.shift_count += 1
            prev = self.gear
            self.gear = min(max(self.gear + change, 0), len(self.gear_max) - 1)
            return self.gear != prev
        return False

    def apply_controls(
        self,
        throttle: float,
        brake: float,
        steering: float,
        dt: float = 1.0,
        track=None,
    ):
        """
        Updates the car's speed and angle based on throttle/brake/steering inputs.
        :param throttle: 0..1 amount of acceleration.
        :param brake: 0..1 braking intensity.
        :param steering: Negative => turn left, Positive => turn right.
        :param dt: Timestep in seconds.
        :param track: Optional track to check for off-road slowdown.
        """
        # Accelerate / Decelerate with gear torque
        gear_factor = 1.0 + 0.5 * self.gear
        if throttle > 0.0:
            self.speed += self.acceleration * gear_factor * throttle * dt
        if brake > 0.0:
            self.speed -= self.acceleration * brake * dt

        # Clamp speed by current gear unless unlimited is enabled
        max_speed = self.gear_max[self.gear]
        if self.speed < 0.0:
            self.speed = 0.0
        elif not self.unlimited and self.speed > max_speed:
            self.speed = max_speed

        # Steering with speed sensitivity
        speed_limit = self.gear_max[self.gear]
        steer_factor = max(0.4, 1.0 - self.speed / (speed_limit * 1.2))
        self.angle += steering * self.turn_rate * steer_factor * dt

        # Update position
        dx = self.speed * math.cos(self.angle) * dt
        dy = self.speed * math.sin(self.angle) * dt
        self.x += dx
        self.y += dy

        # Off-road slowdown
        if track and not track.on_road(self):
            self.speed *= 0.5

        # Surface friction zones
        if track:
            self.speed *= track.surface_friction(self)

    def crash(self) -> None:
        """Stop the car and reset gear when a crash occurs."""

        self.speed = 0.0
        self.gear = 0
