"""Helpers for centerline curve interpolation."""

from __future__ import annotations

from dataclasses import dataclass
import math
from bisect import bisect_left
from typing import List, Tuple


@dataclass
class CurveSegment:
    """Piecewise constant-curvature segment."""

    x: float
    y: float
    curvature: float
    length: float


class TrackCurve:
    """Continuous track centerline built from segments."""

    def __init__(self, segments: List[CurveSegment]):
        self.segments = segments
        self._points: List[Tuple[float, float]] = []
        self._lengths: List[float] = []
        self.total_length = 0.0
        self._build()

    @classmethod
    def from_tuples(cls, data: List[Tuple[float, float, float, float]]) -> "TrackCurve":
        segs = [CurveSegment(*t) for t in data]
        return cls(segs)

    def _build(self) -> None:
        """Precompute polyline points spaced one meter apart."""
        x, y, angle = 0.0, 0.0, 0.0
        self._points.append((x, y))
        for seg in self.segments:
            if seg != self.segments[0]:
                x, y = seg.x, seg.y
            dist = 0.0
            while dist < seg.length:
                step = min(1.0, seg.length - dist)
                if abs(seg.curvature) > 1e-6:
                    radius = 1.0 / seg.curvature
                    dtheta = step * seg.curvature
                    cx = x - radius * math.sin(angle)
                    cy = y + radius * math.cos(angle)
                    angle += dtheta
                    x = cx + radius * math.sin(angle)
                    y = cy - radius * math.cos(angle)
                else:
                    x += step * math.cos(angle)
                    y += step * math.sin(angle)
                dist += step
                self.total_length += step
                self._points.append((x, y))
                self._lengths.append(self.total_length)

    def point_at(self, s: float) -> Tuple[float, float]:
        """Return position ``(x, y)`` at distance ``s`` along the curve."""
        if not self._points:
            return 0.0, 0.0
        s = max(0.0, min(s, self.total_length))
        for i, d in enumerate(self._lengths):
            if d >= s:
                return self._points[i + 1]
        return self._points[-1]

    def tangent_at(self, s: float) -> Tuple[float, float]:
        """Return unit tangent vector at distance ``s`` along the curve."""

        if not self._points:
            return 0.0, 0.0
        s = max(0.0, min(s, self.total_length))
        idx = bisect_left(self._lengths, s)
        idx = min(max(idx, 0), len(self._points) - 2)
        x0, y0 = self._points[idx]
        x1, y1 = self._points[idx + 1]
        dx, dy = x1 - x0, y1 - y0
        norm = math.hypot(dx, dy) or 1.0
        return dx / norm, dy / norm

    def normal_at(self, s: float) -> Tuple[float, float]:
        tx, ty = self.tangent_at(s)
        return -ty, tx
