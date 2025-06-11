import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from super_pole_position.envs.pole_position import PolePositionEnv


def test_offroad_speed():
    env = PolePositionEnv(render_mode="human", mode="race")
    env.reset()
    env.cars[0].y = 1.0  # near edge -> off-road
    env.cars[0].gear = 1
    speed_before = env.cars[0].speed
    env.step((True, False, 0.0))
    assert env.cars[0].speed < env.cars[0].acceleration
    env.close()
