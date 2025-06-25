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
import hashlib
from pathlib import Path
from dataclasses import dataclass

from ..config import load_parity_config
from .track_curve import TrackCurve


_PARITY_CFG = load_parity_config()


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
    """A toroidal track with optional centerline segments and road width."""

    def __init__(
        self,
        width: float = 200.0,
        height: float = 200.0,
        road_width: float = 10.0,
        obstacles: list[Obstacle] | None = None,
        puddles: list[Puddle] | None = None,
        surfaces: list[SurfaceZone] | None = None,
        segments: list[tuple[float, float]] | None = None,
        curve: TrackCurve | None = None,
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
        self.road_width = road_width
        self.obstacles = obstacles or []
        self.puddles = puddles or []
        self.surfaces = surfaces or []
        self.segments = segments or [(0.0, height / 2), (width, height / 2)]
        self.curve = curve
        self._curve_lengths: list[float] = []
        if self.curve:
            self._curve_lengths = list(self.curve._lengths)

        self._hash = self._compute_hash()

    # ------------------------------------------------------------------
    def _compute_hash(self) -> str:
        data = {
            "width": self.width,
            "height": self.height,
            "road_width": self.road_width,
            "obstacles": [
                (o.x, o.y, o.width, o.height, o.billboard) for o in self.obstacles
            ],
            "puddles": [(p.x, p.y, p.radius) for p in self.puddles],
            "surfaces": [
                (s.x, s.y, s.width, s.height, s.friction) for s in self.surfaces
            ],
            "segments": self.segments,
            "curve": getattr(self.curve, "_points", None),
        }
        blob = json.dumps(data, sort_keys=True).encode()
        return hashlib.sha256(blob).hexdigest()

    @property
    def track_hash(self) -> str:
        """Return deterministic hash representing the track."""

        return self._compute_hash()

    # ------------------------------------------------------------------
    @staticmethod
    def get_puddle_factor() -> float:
        """Return slowdown factor for puddles from config."""

        cfg = load_parity_config()
        try:
            return float(cfg["puddle"]["speed_factor"])
        except KeyError as exc:  # pragma: no cover - misconfigured config
            raise KeyError("Missing puddle.speed_factor in config") from exc

    # ------------------------------------------------------------------
    # Geometry helpers
    # ------------------------------------------------------------------
    def y_at(self, x: float) -> float:
        """Return centerline ``y`` position for ``x`` (legacy)."""

        if self.curve:
            pos = self.curve.point_at(x)
            return pos[1]
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
        """Return road angle in radians at ``x`` or distance ``x``."""

        if self.curve:
            tx, ty = self.curve.tangent_at(x)
            return math.atan2(ty, tx)
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

    def is_on_road(self, x: float, y: float) -> bool:
        """Return ``True`` if coordinates are within the paved bounds."""

        if self.curve:
            prog = self.progress((x, y)) * self.curve.total_length
            cx, cy = self.curve.point_at(prog)
            tx, ty = self.curve.normal_at(prog)
            dx = x - cx
            dy = y - cy
            offset = abs(dx * tx + dy * ty)
            return offset <= self.road_width / 2

        center_y = self.y_at(x)
        return abs(y - center_y) <= self.road_width / 2

    def on_road(self, car) -> bool:
        """Return ``True`` if ``car`` is within the paved road bounds."""

        return self.is_on_road(car.x, car.y)

    @classmethod
    def load(cls, name: str) -> "Track":
        path = (
            Path(__file__).resolve().parents[2]
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
            road_w = float(data.get("road_width", 10.0))
            if seg:
                if len(seg[0]) == 4:
                    curve = TrackCurve.from_tuples([tuple(p) for p in seg])
                    width = int(max(p[0] for p in curve._points)) + 1
                    height = int(max(p[1] for p in curve._points)) + 1
                    return cls(
                        width=width,
                        height=height,
                        obstacles=obstacles,
                        puddles=puddles,
                        surfaces=surfaces,
                        segments=None,
                        curve=curve,
                        road_width=road_w,
                    )
                else:
                    width = max(p[0] for p in seg)
                    height = max(p[1] for p in seg)
                    return cls(
                        width=width,
                        height=height,
                        obstacles=obstacles,
                        puddles=puddles,
                        surfaces=surfaces,
                        segments=[tuple(p) for p in seg],
                        road_width=road_w,
                    )
            if obstacles or puddles or surfaces:
                return cls(
                    obstacles=obstacles,
                    puddles=puddles,
                    surfaces=surfaces,
                    road_width=road_w,
                )
        return cls()

    @classmethod
    def load_namco(cls, name: str) -> "Track":
        """Load one of the original Namco tracks by name."""

        path = (
            Path(__file__).resolve().parents[2]
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
            road_w = float(data.get("road_width", 10.0))
            if seg:
                if len(seg[0]) == 4:
                    curve = TrackCurve.from_tuples([tuple(p) for p in seg])
                    width = int(max(p[0] for p in curve._points)) + 1
                    height = int(max(p[1] for p in curve._points)) + 1
                    return cls(
                        width=width,
                        height=height,
                        obstacles=obstacles,
                        puddles=puddles,
                        surfaces=surfaces,
                        segments=None,
                        curve=curve,
                        road_width=road_w,
                    )
                else:
                    width = max(p[0] for p in seg)
                    height = max(p[1] for p in seg)
                    return cls(
                        width=width,
                        height=height,
                        obstacles=obstacles,
                        puddles=puddles,
                        surfaces=surfaces,
                        segments=[tuple(p) for p in seg],
                        road_width=road_w,
                    )
            if obstacles or puddles or surfaces:
                return cls(
                    obstacles=obstacles,
                    puddles=puddles,
                    surfaces=surfaces,
                    road_width=road_w,
                )
        raise FileNotFoundError(name)

    def wrap_position(self, car) -> None:
        """Wrap ``car.x`` around track width while leaving ``y`` unclamped."""
        if self.curve:
            car.x = max(0.0, min(car.x, self.width))
            car.y = max(0.0, min(car.y, self.height))
        else:
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
        if not self.curve:
            dx = min(dx, self.width - dx)
        return math.sqrt(dx * dx + dy * dy)

    def progress(self, car) -> float:
        """Return lap progress 0..1 based on arc length or x position."""
        if self.curve:
            x = car.x if hasattr(car, "x") else car[0]
            y = car.y if hasattr(car, "y") else car[1]
            best = 0.0
            best_dist = float("inf")
            for d, p in zip(self._curve_lengths, self.curve._points[1:]):
                dx = x - p[0]
                dy = y - p[1]
                dist = dx * dx + dy * dy
                if dist < best_dist:
                    best_dist = dist
                    best = d
            return best / self.curve.total_length
        delta = (car.x - self.start_x) % self.width
        return delta / self.width

    def distance_along_track(self, pos) -> float:
        """Return normalized distance 0..1 along track from ``start_x``."""
        if self.curve:
            return self.progress(pos)
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
        return self.base_friction_factor(car)

    # ------------------------------------------------------------------
    def base_friction_factor(self, obj) -> float:
        """Return friction factor for ``obj`` based on surface properties."""

        factor = 1.0

        if self.in_puddle(obj):
            factor *= self.get_puddle_factor()

        for s in self.surfaces:
            if s.x <= obj.x <= s.x + s.width and s.y <= obj.y <= s.y + s.height:
                factor *= s.friction
                break

        return factor

    def friction_factor(self, car) -> float:
        """Return combined friction factor for ``car``."""

        factor = self.surface_friction(car)

        if not self.on_road(car):
            if self.in_puddle(car):
                factor *= float(_PARITY_CFG.get("offroad_factor", 0.5))
            else:
                factor *= float(_PARITY_CFG.get("offroad_speed_factor", 0.5))

        return factor

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
