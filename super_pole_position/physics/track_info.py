from __future__ import annotations

"""Track information utilities."""

from dataclasses import dataclass
import json
import math
from pathlib import Path
from typing import List, Tuple


@dataclass
class TrackInfo:
    """Simple container for precomputed track geometry."""

    length_meters: float
    segments: List[Tuple[float, float]]
    curvature: List[float]


def load_track_info(name: str = "fuji_namco") -> TrackInfo:
    """Load track info from an asset json file.

    Parameters
    ----------
    name:
        Track filename without extension.

    Returns
    -------
    TrackInfo
        Parsed track data with cumulative length and curvature.
    """

    path = Path(__file__).resolve().parents[2] / "assets" / "tracks" / f"{name}.json"
    data = json.loads(path.read_text())
    pts = [tuple(p) for p in data.get("segments", [])]
    if len(pts) < 2:
        raise ValueError("track requires at least two points")

    length = 0.0
    curvatures: List[float] = []

    for i in range(len(pts)):
        p_prev = pts[i - 1]
        p_curr = pts[i]
        p_next = pts[(i + 1) % len(pts)]

        dx1 = p_curr[0] - p_prev[0]
        dy1 = p_curr[1] - p_prev[1]
        dx2 = p_next[0] - p_curr[0]
        dy2 = p_next[1] - p_curr[1]

        seg_len = math.hypot(dx2, dy2)
        length += seg_len

        angle1 = math.atan2(dy1, dx1)
        angle2 = math.atan2(dy2, dx2)
        dtheta = angle2 - angle1
        while dtheta > math.pi:
            dtheta -= 2 * math.pi
        while dtheta < -math.pi:
            dtheta += 2 * math.pi
        curv = dtheta / seg_len if seg_len else 0.0
        curvatures.append(curv)

    return TrackInfo(length_meters=length, segments=pts, curvature=curvatures)
