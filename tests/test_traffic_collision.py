import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from super_pole_position.envs.pole_position import PolePositionEnv


def test_traffic_collision():
    env = PolePositionEnv(render_mode="human", mode="race")
    env.reset()
    env.start_timer = 0
    env.cars[0].gear = 1
    env.cars[0].y = env.track.height / 2
    env.cars[0].x = env.traffic[0].x - 1
    env.step((True, False, 0.0))
    assert env.crashes >= 1
    env.close()
