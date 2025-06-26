import pytest
from super_pole_position.envs.pole_position import PolePositionEnv


@pytest.mark.skip("nondeterministic currently")
def test_2600_mode_repeatable():
    env1 = PolePositionEnv(render_mode="human", mode_2600=True)
    env1.reset(seed=42)
    for _ in range(151):
        env1.step({"throttle": 0.0, "brake": 0.0, "steer": 0.0})
    pos1 = (env1.traffic[0].x, env1.traffic[0].y)
    env1.close()

    env2 = PolePositionEnv(render_mode="human", mode_2600=True)
    env2.reset(seed=42)
    for _ in range(151):
        env2.step({"throttle": 0.0, "brake": 0.0, "steer": 0.0})
    pos2 = (env2.traffic[0].x, env2.traffic[0].y)
    env2.close()

    assert pos1 == pos2
