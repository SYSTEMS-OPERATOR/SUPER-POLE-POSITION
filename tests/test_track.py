import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from super_pole_position.physics.track import Track
from super_pole_position.physics.car import Car


def test_wrap_position():
    track = Track(width=100.0, height=100.0)
    car = Car(x=110.0, y=-5.0)
    track.wrap_position(car)
    assert 0.0 <= car.x < track.width
    assert 0.0 <= car.y < track.height


def test_distance():
    track = Track(width=100.0, height=100.0)
    car1 = Car(x=10.0, y=10.0)
    car2 = Car(x=90.0, y=10.0)
    dist = track.distance(car1, car2)
    # shortest distance across wrap is 20
    assert dist == 20.0
