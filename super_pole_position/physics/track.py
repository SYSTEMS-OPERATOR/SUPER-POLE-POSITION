#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 MIND INTERFACES, INC. All rights reserved.
# Licensed under the MIT License.

"""
track.py
Description: Module for Super Pole Position.
"""



import math
import json
from pathlib import Path
from dataclasses import dataclass


@dataclass
class Puddle:
    """Circular puddle causing traction loss."""

    x: float
    y: float
    radius: float


@dataclass
class Obstacle:
    """Static obstacle placed on the track."""

    x: float
    y: float
    width: float
    height: float

class Track:
    """A toroidal track with a defined length or 2D bounding box."""

    def __init__(self, width=200.0, height=200.0, obstacles=None, puddles=None):
        """
        For a 2D track: we treat the space as a wraparound.
        :param width: Width of the track space.
        :param height: Height of the track space.
        """
        self.width = width
        self.height = height
        self.start_x = 0.0
        self.obstacles: list[Obstacle] = obstacles or []
        self.puddles: list[Puddle] = puddles or []

    @classmethod
    def load(cls, name: str) -> "Track":
        path = Path(__file__).resolve().parent.parent / "assets" / "tracks" / f"{name}.json"
        if path.exists():
            data = json.loads(path.read_text())
            seg = data.get("segments", [])
            obstacles = [Obstacle(**o) for o in data.get("obstacles", [])]
            puddles = [Puddle(**p) for p in data.get("puddles", [])]
            if seg:
                width = max(p[0] for p in seg)
                height = max(p[1] for p in seg)
                return cls(
                    width=width,
                    height=height,
                    obstacles=obstacles,
                    puddles=puddles,
                )
            if obstacles or puddles:
                return cls(obstacles=obstacles, puddles=puddles)
        return cls()

    @classmethod
    def load_namco(cls, name: str) -> "Track":
        """Load one of the original Namco tracks by name."""

        path = Path(__file__).resolve().parent.parent / "assets" / "tracks" / f"{name}.json"
        if path.exists():
            data = json.loads(path.read_text())
            seg = data.get("segments", [])
            obstacles = [Obstacle(**o) for o in data.get("obstacles", [])]
            puddles = [Puddle(**p) for p in data.get("puddles", [])]
            if seg:
                width = max(p[0] for p in seg)
                height = max(p[1] for p in seg)
                return cls(
                    width=width,
                    height=height,
                    obstacles=obstacles,
                    puddles=puddles,
                )
            if obstacles or puddles:
                return cls(obstacles=obstacles, puddles=puddles)
        raise FileNotFoundError(name)

    def wrap_position(self, car):
        """
        Wraps the car's position if it goes beyond track boundaries.
        This simulates a toroidal environment (like Pac-Man).
        """
        if car.x < 0.0:
            car.x += self.width
        elif car.x >= self.width:
            car.x -= self.width

        if car.y < 0.0:
            car.y += self.height
        elif car.y >= self.height:
            car.y -= self.height

    def distance(self, car1, car2):
        """
        Computes the shortest distance between two cars in a toroidal space.
        Could be used for collision detection or AI awareness.
        """
        dx = abs(car1.x - car2.x)
        dy = abs(car1.y - car2.y)

        # On a torus, distance wraps around
        dx = min(dx, self.width - dx)
        dy = min(dy, self.height - dy)

        return math.sqrt(dx * dx + dy * dy)

    def progress(self, car) -> float:
        """Return lap progress 0..1 based on x position."""
        delta = (car.x - self.start_x) % self.width
        return delta / self.width

    def in_puddle(self, car) -> bool:
        """Return True if ``car`` is inside a puddle."""

        for p in self.puddles:
            dx = car.x - p.x
            dy = car.y - p.y
            if dx * dx + dy * dy <= p.radius * p.radius:
                return True
        return False
