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
class SurfaceZone:
    """Rectangular zone with friction modifier."""

    x: float
    y: float
    width: float
    height: float
    friction: float = 0.8


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
    billboard: bool = False

class Track:
    """A toroidal track with a defined length or 2D bounding box."""

    def __init__(self, width=200.0, height=200.0, obstacles=None, puddles=None, surfaces=None):
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
        self.surfaces: list[SurfaceZone] = surfaces or []

    @classmethod
    def load(cls, name: str) -> "Track":
        path = Path(__file__).resolve().parent.parent / "assets" / "tracks" / f"{name}.json"
        if path.exists():
            data = json.loads(path.read_text())
            seg = data.get("segments", [])
            obstacles = [Obstacle(**o) for o in data.get("obstacles", [])]
            puddles = [Puddle(**p) for p in data.get("puddles", [])]
            surfaces = [SurfaceZone(**s) for s in data.get("surfaces", [])]
            surfaces = [SurfaceZone(**s) for s in data.get("surfaces", [])]
            surfaces = [SurfaceZone(**s) for s in data.get("surfaces", [])]
            if seg:
                width = max(p[0] for p in seg)
                height = max(p[1] for p in seg)
                return cls(
                    width=width,
                    height=height,
                    obstacles=obstacles,
                    puddles=puddles,
                    surfaces=surfaces,
                )
            if obstacles or puddles or surfaces:
                return cls(obstacles=obstacles, puddles=puddles, surfaces=surfaces)
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
            surfaces = [SurfaceZone(**s) for s in data.get("surfaces", [])]
            if seg:
                width = max(p[0] for p in seg)
                height = max(p[1] for p in seg)
                return cls(
                    width=width,
                    height=height,
                    obstacles=obstacles,
                    puddles=puddles,
                    surfaces=surfaces,
                )
            if obstacles or puddles or surfaces:
                return cls(obstacles=obstacles, puddles=puddles, surfaces=surfaces)
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

    def surface_friction(self, car) -> float:
        """Return friction coefficient for ``car`` based on surface zones."""

        for s in self.surfaces:
            if (
                s.x <= car.x <= s.x + s.width
                and s.y <= car.y <= s.y + s.height
            ):
                return s.friction
        return 1.0

    def billboard_hit(self, car) -> bool:
        """Remove billboard obstacle when ``car`` collides with it."""

        for obs in list(self.obstacles):
            if not getattr(obs, "billboard", False):
                continue
            if (
                abs(car.x - obs.x) <= obs.width / 2
                and abs(car.y - obs.y) <= obs.height / 2
            ):
                self.obstacles.remove(obs)
                return True
        return False
