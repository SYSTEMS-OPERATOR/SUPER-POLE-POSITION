import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from super_pole_position.envs.pole_position import PolePositionEnv


def test_checkpoint_timer_rollover():
    env = PolePositionEnv(render_mode="human", mode="race")
    env.reset()
    env.start_timer = 0
    env.cars[0].gear = 1
    before = env.remaining_time
    for _ in range(5):
        env.cars[0].apply_controls(True, False, 0.0)
        env.step((False, False, 0.0))
        if env.remaining_time > before:
            break
    assert env.remaining_time > before
    env.close()
