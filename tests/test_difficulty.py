import pytest
from super_pole_position.envs.pole_position import PolePositionEnv


def test_difficulty_time_settings():
    easy = PolePositionEnv(render_mode="human", difficulty="easy")
    normal = PolePositionEnv(render_mode="human", difficulty="normal")
    hard = PolePositionEnv(render_mode="human", difficulty="hard")

    assert easy.time_limit > normal.time_limit > hard.time_limit
    assert easy.time_bonus > normal.time_bonus > hard.time_bonus

    easy.close()
    normal.close()
    hard.close()
