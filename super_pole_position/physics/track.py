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
    """A toroidal track with optional centerline segments."""

    def __init__(
        self,
        width: float = 200.0,
        height: float = 200.0,
        obstacles: list[Obstacle] | None = None,
        puddles: list[Puddle] | None = None,
        surfaces: list[SurfaceZone] | None = None,
        segments: list[tuple[float, float]] | None = None,
    ) -> None:
        """Create a simple wraparound track.

        Parameters
        ----------
        width:
            Horizontal span of the track.
        height:
            Vertical span of the track.
        """

        self.width = width
        self.height = height
        self.start_x = 0.0
        self.obstacles = obstacles or []
        self.puddles = puddles or []
        self.surfaces = surfaces or []
        self.segments = segments or [(0.0, height / 2), (width, height / 2)]

    # ------------------------------------------------------------------
    # Geometry helpers
    # ------------------------------------------------------------------
    def y_at(self, x: float) -> float:
        """Return centerline ``y`` position for ``x``."""

        if not self.segments:
            return self.height / 2
        t = (x % self.width) / self.width
        seg_pos = t * (len(self.segments) - 1)
        i = int(seg_pos)
        frac = seg_pos - i
        p0 = self.segments[i]
        p1 = self.segments[(i + 1) % len(self.segments)]
        return p0[1] + (p1[1] - p0[1]) * frac

    def angle_at(self, x: float) -> float:
        """Return road angle in radians at ``x``."""

        if not self.segments:
            return 0.0
        t = (x % self.width) / self.width
        seg_pos = t * (len(self.segments) - 1)
        i = int(seg_pos)
        p0 = self.segments[i]
        p1 = self.segments[(i + 1) % len(self.segments)]
        dy = p1[1] - p0[1]
        dx = p1[0] - p0[0]
        return math.atan2(dy, dx)

    @classmethod
    def load(cls, name: str) -> "Track":
        path = (
            Path(__file__).resolve().parent.parent
            / "assets"
            / "tracks"
            / f"{name}.json"
        )
        if path.exists():
            try:
                data = json.loads(path.read_text())
            except Exception:
                return cls()
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
                    segments=[tuple(p) for p in seg],
                )
            if obstacles or puddles or surfaces:
                return cls(
                    obstacles=obstacles,
                    puddles=puddles,
                    surfaces=surfaces,
                )
        return cls()

    @classmethod
    def load_namco(cls, name: str) -> "Track":
        """Load one of the original Namco tracks by name."""

        path = (
            Path(__file__).resolve().parent.parent
            / "assets"
            / "tracks"
            / f"{name}.json"
        )
        if path.exists():
            try:
                data = json.loads(path.read_text())
            except Exception:
                return cls()
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
                    segments=[tuple(p) for p in seg],
                )
            if obstacles or puddles or surfaces:
                return cls(
                    obstacles=obstacles,
                    puddles=puddles,
                    surfaces=surfaces,
                )
        raise FileNotFoundError(name)

    def wrap_position(self, car) -> None:
        """Wrap ``car.x`` around track width while leaving ``y`` unclamped."""

        if car.x < 0.0:
            car.x += self.width
        elif car.x >= self.width:
            car.x -= self.width

    def distance(self, car1, car2):
        """
        Computes the shortest distance between two cars in a toroidal space.
        Could be used for collision detection or AI awareness.
        """
        dx = abs(car1.x - car2.x)
        dy = abs(car1.y - car2.y)

        dx = min(dx, self.width - dx)

        return math.sqrt(dx * dx + dy * dy)

    def progress(self, car) -> float:
        """Return lap progress 0..1 based on x position."""
        delta = (car.x - self.start_x) % self.width
        return delta / self.width

    def distance_along_track(self, pos) -> float:
        """Return normalized distance 0..1 along track from ``start_x``."""
        x = pos.x if hasattr(pos, "x") else pos[0]
        delta = (x - self.start_x) % self.width
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
            if s.x <= car.x <= s.x + s.width and s.y <= car.y <= s.y + s.height:
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
