import math
import json
import pathlib
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.physics.track import Track

T = Track()

def test_total_length():
    j = json.loads(pathlib.Path("src/data/track_fuji.json").read_text())
    assert math.isclose(sum(s["length"] for s in j), T.lap_length, abs_tol=1e-3)

def test_angle_wrap():
    assert math.isclose(T.angle_at(0), T.angle_at(T.lap_length), rel_tol=1e-6)

def test_curvature_left_right():
    left_x = next(seg.start_x for seg in T.segments if seg.type == "left")
    right_x = next(seg.start_x for seg in T.segments if seg.type == "right")
    assert T.curvature_at(left_x) > 0
    assert T.curvature_at(right_x) < 0
