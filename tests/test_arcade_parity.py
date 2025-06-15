import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from super_pole_position.envs.pole_position import PolePositionEnv
from super_pole_position.physics.track import Track, Puddle


def measure_puddle_ratio() -> float:
    env = PolePositionEnv(render_mode="human")
    env.track = Track(width=200.0, height=200.0, puddles=[Puddle(x=50, y=50, radius=10)])
    env.reset()
    env.step({"throttle": True, "brake": False, "steer": 0.0})
    pre = env.cars[0].speed
    env.step({"throttle": False, "brake": False, "steer": 0.0})
    post = env.cars[0].speed
    return post / pre


def test_puddle_slowdown_improved():
    with open("benchmarks/baseline_puddle.txt") as fh:
        baseline_ratio = float(fh.read().split()[1])
    ratio = measure_puddle_ratio()
    assert ratio < baseline_ratio - 0.04
