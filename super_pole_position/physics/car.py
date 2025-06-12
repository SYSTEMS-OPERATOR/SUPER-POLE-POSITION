"""
car.py

Defines a simple Car class with basic arcade-like physics:
- x, y coordinates
- speed, angle
- apply_controls() method
"""

import math

class Car:
    """A basic arcade-style car with position, speed, angle, acceleration."""
    length = 2.0
    width = 1.0

    def __init__(self, x=0.0, y=0.0, angle=0.0, speed=0.0):
        self.x = x
        self.y = y
        self.angle = angle  # Radians; 0 means facing 'east' by convention
        self.speed = speed
        self.acceleration = 2.0
        # Two gear ratios: index 0=LOW, 1=HIGH
        self.gear_max = [8.0, 15.0]
        self.gear = 0
        self.max_speed = self.gear_max[-1]
        self.turn_rate = 2.0  # rad/sec
        self.shift_count = 0

    def shift(self, change: int) -> None:
        """Change gear by ``change`` amount (e.g. -1, 0, +1)."""
        if change:
            self.shift_count += 1
            self.gear = min(max(self.gear + change, 0), len(self.gear_max) - 1)

    def apply_controls(
        self,
        throttle: bool,
        brake: bool,
        steering: float,
        dt: float = 1.0,
        track=None,
    ):
        """
        Updates the car's speed and angle based on throttle/brake/steering inputs.
        :param throttle: If True, accelerate.
        :param brake: If True, decelerate.
        :param steering: Negative => turn left, Positive => turn right.
        :param dt: Timestep in seconds.
        :param track: Optional track to check for off-road slowdown.
        """
        # Accelerate / Decelerate
        if throttle:
            self.speed += self.acceleration * dt
        if brake:
            self.speed -= self.acceleration * dt

        # Clamp speed by current gear
        max_speed = self.gear_max[self.gear]
        if self.speed < 0.0:
            self.speed = 0.0
        elif self.speed > max_speed:
            self.speed = max_speed

        # Steering
        self.angle += steering * self.turn_rate * dt

        # Update position
        dx = self.speed * math.cos(self.angle) * dt
        dy = self.speed * math.sin(self.angle) * dt
        self.x += dx
        self.y += dy

        # Off-road slowdown
        if track and (self.y < 5 or self.y > track.height - 5):
            self.speed *= 0.5

    def crash(self) -> None:
        """Stop the car and reset gear when a crash occurs."""

        self.speed = 0.0
        self.gear = 0

