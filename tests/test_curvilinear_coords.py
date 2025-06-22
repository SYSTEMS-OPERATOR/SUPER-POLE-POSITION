import importlib.util
import os
import pathlib
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

MODULE_PATH = pathlib.Path(__file__).resolve().parents[1] / "super_pole_position" / "physics.py"
spec = importlib.util.spec_from_file_location("super_pole_position.physics_module", MODULE_PATH)
sp_physics = importlib.util.module_from_spec(spec)
sys.modules["super_pole_position.physics_module"] = sp_physics
spec.loader.exec_module(sp_physics)  # type: ignore

from super_pole_position.physics.track import Track
from super_pole_position.physics.track_curve import TrackCurve, CurveSegment


def test_curvilinear_coords_straight():
    track = Track(width=100.0, height=50.0, road_width=10.0)
    x = 20.0
    y = track.y_at(x) + 3.0
    s, d = sp_physics.curvilinear_coords(track, x, y)
    assert pytest.approx(s) == (x - track.start_x) % track.width
    assert pytest.approx(d) == 3.0


def test_curvilinear_coords_curved():
    segs = [CurveSegment(0.0, 0.0, 0.05, 10.0), CurveSegment(10.0, 0.0, 0.0, 10.0)]
    curve = TrackCurve(segs)
    track = Track(width=20.0, height=20.0, segments=None, curve=curve)
    s = 5.0
    d = 2.0
    cx, cy = curve.point_at(s)
    nx, ny = curve.normal_at(s)
    x = cx + nx * d
    y = cy + ny * d
    calc_s, calc_d = sp_physics.curvilinear_coords(track, x, y)
    assert pytest.approx(calc_s, abs=0.1) == pytest.approx(s, abs=0.1)
    assert pytest.approx(calc_d, abs=1e-6) == pytest.approx(d, abs=1e-6)
