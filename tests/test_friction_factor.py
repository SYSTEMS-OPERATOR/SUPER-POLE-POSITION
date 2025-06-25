from super_pole_position.physics.car import Car
from super_pole_position.physics.track import Track, Puddle, SurfaceZone


def test_friction_factor_combined():
    zone = SurfaceZone(x=5, y=5, width=10, height=10, friction=0.8)
    puddle = Puddle(x=10, y=10, radius=5)
    track = Track(width=20, height=20, puddles=[puddle], surfaces=[zone])
    car = Car(x=10, y=10)
    expected = track.get_puddle_factor() * zone.friction
    assert track.friction_factor(car) == expected


def test_friction_factor_clear():
    track = Track(width=20, height=20)
    car = Car(x=1, y=1)
    assert track.friction_factor(car) == 1.0
