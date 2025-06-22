from __future__ import annotations

import json
import math
from bisect import bisect_right
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, List, Optional

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@dataclass
class Segment:
    start_x: float
    end_x: float
    type: str
    length: float
    radius: Optional[float]
    base_heading: float
    arc_angle: float


@dataclass
class TrackObject:
    x: float
    y: float
    meta: dict


class Track:
    def __init__(self, json_path: Path = DATA_DIR / "track_fuji.json") -> None:
        data = json.loads(Path(json_path).read_text())

        self.segments: List[Segment] = []
        self.objects: List[TrackObject] = []
        start_x = 0.0
        heading = 0.0

        for seg in data:
            length = float(seg["length"])
            seg_type = seg["type"]
            radius = seg.get("radius")
            if seg_type == "straight":
                arc = 0.0
            else:
                sign = 1.0 if seg_type == "left" else -1.0
                arc = sign * (length / float(radius))
            self.segments.append(
                Segment(
                    start_x=start_x,
                    end_x=start_x + length,
                    type=seg_type,
                    length=length,
                    radius=radius,
                    base_heading=heading,
                    arc_angle=arc,
                )
            )
            for obj in seg.get("objects", []):
                ox = start_x + float(obj.get("x", 0))
                oy = float(obj.get("y", 0))
                meta = {k: v for k, v in obj.items() if k not in {"x", "y"}}
                self.objects.append(TrackObject(ox, oy, meta))
            heading += arc
            start_x += length

        self._lap_length = start_x
        self._starts = [seg.start_x for seg in self.segments]

    # ------------------------------------------------------------------
    @property
    def lap_length(self) -> float:
        return self._lap_length

    # ------------------------------------------------------------------
    def _segment_index(self, x: float) -> int:
        x_mod = x % self._lap_length
        return bisect_right(self._starts, x_mod) - 1

    # ------------------------------------------------------------------
    def angle_at(self, x: float) -> float:
        idx = self._segment_index(x)
        seg = self.segments[idx]
        heading = seg.base_heading
        if seg.type != "straight":
            sign = 1.0 if seg.type == "left" else -1.0
            delta = (x % self._lap_length - seg.start_x) / float(seg.radius)
            heading += sign * delta
        return heading

    # ------------------------------------------------------------------
    def curvature_at(self, x: float) -> float:
        seg = self.segments[self._segment_index(x)]
        if seg.type == "straight" or not seg.radius:
            return 0.0
        sign = 1.0 if seg.type == "left" else -1.0
        return sign / float(seg.radius)

    # ------------------------------------------------------------------
    def objects_near(self, x: float, range_m: float) -> Iterator[TrackObject]:
        x_mod = x % self._lap_length
        for obj in self.objects:
            forward = (obj.x - x_mod + self._lap_length) % self._lap_length
            back = (x_mod - obj.x + self._lap_length) % self._lap_length
            if min(forward, back) < range_m:
                yield obj


"""
── Original Panda3D logic (grid_leader/track.py) ─────────────────────────
def heading_at(self, x):
    heading = 0.0
    for seg in self.segments:
        if x < seg.length:
            if seg.type != STRAIGHT:
                heading += (x/seg.radius) * seg.direction  # +left, ‑right
            break
        heading += seg.arc_angle
        x -= seg.length
    return heading

def curvature_at(self, x):
    seg = self.segment_at(x)
    if seg.type == STRAIGHT:
        return 0.0
    return seg.direction / seg.radius  # dir = ±1

── Minimal Pygame translation guideline ────────────────────────────────
# Load json; pre‑compute cumulative_x.
# angle_at(x):
#   idx = bisect_right(self.cumulative, x_mod)‑1
#   seg  = self.segments[idx]
#   if seg['type'] != 'straight':
#       delta = (x_mod - seg['start_x']) / seg['radius']
#       add    = delta if seg['type']=='left' else -delta
#   heading = seg['base_heading'] + add
# curvature_at(x) analogous.
"""
