import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from super_pole_position.physics.car import Car


def test_shift_changes_max_speed():
    car = Car()
    # low gear max ~8
    car.apply_controls(True, False, 0.0, dt=1.0)
    assert car.speed <= car.gear_max[0]
    car.shift(1)
    for _ in range(10):
        car.apply_controls(True, False, 0.0, dt=1.0)
    assert car.speed <= car.gear_max[1]
