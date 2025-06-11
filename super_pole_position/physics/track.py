"""
track.py

Implements a simple toroidal track or 'infinite' environment.
Optionally, can be extended with segment-based or procedural generation.
"""

import math
import json
from pathlib import Path

class Track:
    """A toroidal track with a defined length or 2D bounding box."""
    def __init__(self, width=200.0, height=200.0):
        """
        For a 2D track: we treat the space as a wraparound.
        :param width: Width of the track space.
        :param height: Height of the track space.
        """
        self.width = width
        self.height = height
        self.start_x = 0.0

    @classmethod
    def load(cls, name: str) -> "Track":
        path = Path(__file__).resolve().parent.parent / "assets" / "tracks" / f"{name}.json"
        if path.exists():
            data = json.loads(path.read_text())
            seg = data.get("segments", [])
            if seg:
                width = max(p[0] for p in seg)
                height = max(p[1] for p in seg)
                return cls(width=width, height=height)
        return cls()

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
