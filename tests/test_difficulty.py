import os
import importlib
from super_pole_position.envs.pole_position import PolePositionEnv


def _load_env() -> None:
    import super_pole_position.envs.pole_position as pp
    importlib.reload(pp)
    globals()["PolePositionEnv"] = pp.PolePositionEnv


def test_expert_time_limit() -> None:
    os.environ["FAST_TEST"] = "0"
    _load_env()
    env = PolePositionEnv(render_mode="human", difficulty="expert")
    assert env.time_limit == 75.0
    env.close()
    os.environ["FAST_TEST"] = "1"
    _load_env()


def test_beginner_time_limit_qualify() -> None:
    os.environ["FAST_TEST"] = "0"
    _load_env()
    env = PolePositionEnv(render_mode="human", mode="qualify", difficulty="beginner")
    assert env.time_limit == 73.0
    env.close()
    os.environ["FAST_TEST"] = "1"
    _load_env()

