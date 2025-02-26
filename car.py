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
    def __init__(self, x=0.0, y=0.0, angle=0.0, speed=0.0):
        self.x = x
        self.y = y
        self.angle = angle  # Radians; 0 means facing 'east' by convention
        self.speed = speed
        self.acceleration = 2.0
        self.max_speed = 15.0
        self.turn_rate = 2.0  # rad/sec

    def apply_controls(self, throttle: bool, brake: bool, steering: float, dt: float = 1.0):
        """
        Updates the car's speed and angle based on throttle/brake/steering inputs.
        :param throttle: If True, accelerate.
        :param brake: If True, decelerate.
        :param steering: Negative => turn left, Positive => turn right.
        :param dt: Timestep in seconds.
        """
        # Accelerate / Decelerate
        if throttle:
            self.speed += self.acceleration * dt
        if brake:
            self.speed -= self.acceleration * dt

        # Clamp speed
        if self.speed < 0.0:
            self.speed = 0.0
        elif self.speed > self.max_speed:
            self.speed = self.max_speed

        # Steering
        self.angle += steering * self.turn_rate * dt

        # Update position
        dx = self.speed * math.cos(self.angle) * dt
        dy = self.speed * math.sin(self.angle) * dt
        self.x += dx
        self.y += dy
