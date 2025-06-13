import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from super_pole_position.envs.pole_position import PolePositionEnv


def test_traffic_ai_pathing():
    env = PolePositionEnv(render_mode="human", mode="race")
    env.reset()
    env.start_timer = 0
    car = env.traffic[0]
    car.y = 1.0  # force off center
    start_offset = abs(car.y - env.track.height / 2)
    for _ in range(10):
        env.step((False, False, 0.0))
    end_offset = abs(car.y - env.track.height / 2)
    assert end_offset < start_offset
    env.close()


def test_traffic_looping():
    env = PolePositionEnv(render_mode="human", mode="race")
    env.reset()
    env.start_timer = 0
    car = env.traffic[0]
    car.x = env.track.width + 5
    env.step((False, False, 0.0))
    assert 0.0 <= car.x < env.track.width
    env.close()
