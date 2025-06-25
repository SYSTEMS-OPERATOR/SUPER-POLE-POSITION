"""Unit tests for Track.friction_factor helper."""

from super_pole_position.physics.car import Car
from super_pole_position.physics.track import Track, Puddle, SurfaceZone
from super_pole_position.config import load_parity_config


def test_offroad_factor():
    track = Track(width=50, height=50)
    car = Car(x=0.0, y=0.0)
    factor = track.friction_factor(car)
    cfg = load_parity_config()
    assert factor == cfg.get("offroad_speed_factor", 0.5)


def test_puddle_factor():
    track = Track(width=50, height=50, puddles=[Puddle(x=25, y=25, radius=5)])
    car = Car(x=25, y=25)
    assert track.friction_factor(car) == track.get_puddle_factor()


def test_surface_zone_factor() -> None:
    zone = SurfaceZone(x=20, y=22, width=5, height=5, friction=0.4)
    track = Track(width=50, height=50, surfaces=[zone])
    car = Car(x=22, y=24)
    assert track.friction_factor(car) == zone.friction
