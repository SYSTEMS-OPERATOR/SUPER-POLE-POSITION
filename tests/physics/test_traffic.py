import random

from src.physics.car import Car
from src.physics.track import Track
from src.physics.traffic_car import TrafficCar


class DummyPlayer(Car):
    pass


def setup():
    track = Track()
    player = DummyPlayer()
    player.x = 1000
    player.y = 0
    player.speed_kmh = 250
    return track, player


def test_lane_switch():
    trk, pl = setup()
    tc = TrafficCar(trk, pl, rng=random.Random(0))
    tc.x = (pl.x + 20) % trk.lap_length
    tc.y = pl.y
    for _ in range(int(0.35 / (1 / 60))):
        tc.update(1 / 60)
    assert tc.lane in [-1, 1]
    assert abs(tc.y) == 2.5


def test_respawn():
    trk, pl = setup()
    tc = TrafficCar(trk, pl, rng=random.Random(1))
    tc.x = (pl.x - 210) % trk.lap_length
    tc.update(1 / 60)
    ahead = (tc.x - pl.x + trk.lap_length) % trk.lap_length
    assert 299 <= ahead <= 301
