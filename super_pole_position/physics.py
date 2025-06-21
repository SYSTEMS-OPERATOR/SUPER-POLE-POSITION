"""Physics helpers used by the arcade-faithful build."""

from typing import Tuple

from .physics.track import Track


def curvilinear_coords(track: Track, x: float, y: float) -> Tuple[float, float]:
    """Return ``(s, d)`` coordinates for position on ``track``."""

    if track.curve is None:
        s = (x - track.start_x) % track.width
        center_y = track.y_at(x)
        d = y - center_y
        return s, d

    prog = track.progress((x, y)) * track.curve.total_length
    cx, cy = track.curve.point_at(prog)
    nx, ny = track.curve.normal_at(prog)
    d = (x - cx) * nx + (y - cy) * ny
    return prog, d
