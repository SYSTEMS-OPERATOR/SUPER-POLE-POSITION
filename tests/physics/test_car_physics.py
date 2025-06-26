import math
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.physics.car import Car


def run_to_speed(target_kmh):
    c = Car()
    steps = 0
    while c.speed_kmh < target_kmh - 1:
        c.update(1.0, 0.0)
        steps += 1
        assert steps < 5000
    return steps / 60


def test_0_100_time():
    t = run_to_speed(100)
    assert 3.5 < t < 5.0


def test_top_speed():
    c = Car()
    for _ in range(60 * 6):
        c.update(1.0, 0.0)
    assert math.isclose(c.speed_kmh, 318, rel_tol=0.02)


def test_steering_limit():
    c = Car()
    c.speed_kmh = 320
    c.update(1.0, 1.0)
    assert c.a_lat <= 0.8 * 9.81 * 1.05


def test_shift_count_increments():
    car = Car()
    assert car.shift_count == 0
    car.shift_high()
    assert car.shift_count == 1
    car.shift_low()
    assert car.shift_count == 2
