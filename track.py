"""
track.py

Implements a simple toroidal track or 'infinite' environment.
Optionally, can be extended with segment-based or procedural generation.
"""

import math
from typing import List, Tuple

class Track:
    """A toroidal track with optional waypoints representing a race course."""

    def __init__(
        self,
        width: float = 200.0,
        height: float = 200.0,
        waypoints: List[Tuple[float, float]] | None = None,
    ) -> None:
        """Create a track.

        Parameters
        ----------
        width, height:
            Define the bounds of the toroidal space.
        waypoints:
            Ordered list of ``(x, y)`` coordinates describing the race course.
            If ``None`` a simple rectangular circuit is generated.
        """

        self.width = width
        self.height = height

        if waypoints is None:
            pad = min(width, height) * 0.1
            waypoints = [
                (pad, pad),
                (width - pad, pad),
                (width - pad, height - pad),
                (pad, height - pad),
            ]

        self.waypoints: List[Tuple[float, float]] = waypoints

        # Pre-compute segment lengths for progress calculations
        self._segment_lengths: List[float] = []
        self.total_length = 0.0
        for i in range(len(self.waypoints)):
            p1 = self.waypoints[i]
            p2 = self.waypoints[(i + 1) % len(self.waypoints)]
            seg_len = math.dist(p1, p2)
            self._segment_lengths.append(seg_len)
            self.total_length += seg_len

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

    def progress_along_course(self, car) -> float:
        """Return fractional progress (0..1) of a car along the course."""
        x, y = car.x, car.y

        best_dist = float("inf")
        best_progress = 0.0
        cumulative = 0.0
        for i, seg_len in enumerate(self._segment_lengths):
            p1 = self.waypoints[i]
            p2 = self.waypoints[(i + 1) % len(self.waypoints)]
            # vector from p1 to p2
            vx = p2[0] - p1[0]
            vy = p2[1] - p1[1]
            seg_len_sq = seg_len * seg_len
            if seg_len_sq == 0:
                continue
            # projection factor t on segment
            t = ((x - p1[0]) * vx + (y - p1[1]) * vy) / seg_len_sq
            t = max(0.0, min(1.0, t))
            proj_x = p1[0] + t * vx
            proj_y = p1[1] + t * vy
            dist = math.dist((x, y), (proj_x, proj_y))
            if dist < best_dist:
                best_dist = dist
                best_progress = cumulative + t * seg_len
            cumulative += seg_len

        if self.total_length == 0:
            return 0.0
        return best_progress / self.total_length
