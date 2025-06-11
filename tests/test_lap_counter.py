import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from super_pole_position.envs.pole_position import PolePositionEnv


def test_lap_counter():
    env = PolePositionEnv(render_mode="human", mode="race")
    env.reset()
    env.start_timer = 0
    for i in range(4):
        env.cars[0].x = env.track.start_x - 1
        env.step((False, False, 0.0))
        env.cars[0].x = env.track.start_x + 1
        env.step((False, False, 0.0))
    assert env.lap >= 4
    env.close()
