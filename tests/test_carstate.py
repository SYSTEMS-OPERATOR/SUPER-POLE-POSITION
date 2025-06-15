from super_pole_position.physics.state import CarState
from super_pole_position.physics.track import Track


def test_carstate_defaults():
    cs = CarState(x=1.0, y=2.0, speed=3.0, angle=0.5)
    assert cs.lap == 0
    assert cs.damage == 0.0
    assert cs.x == 1.0


def test_distance_along_track():
    track = Track(width=100.0, height=100.0)
    track.start_x = 10.0
    d = track.distance_along_track((60.0, 0.0))
    assert d == 0.5
