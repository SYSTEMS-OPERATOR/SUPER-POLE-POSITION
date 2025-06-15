import importlib
import pytest  # noqa: F401


def test_hyper_mode_spawns_and_uncaps(monkeypatch, tmp_path):
    monkeypatch.setenv("HYPER_MODE", "1")
    module = importlib.import_module("super_pole_position.envs.pole_position")
    importlib.reload(module)
    env = module.PolePositionEnv(render_mode="human")
    env.reset()
    monkeypatch.setattr(module, "random", lambda: 0.0)
    start_obstacles = len(env.track.obstacles)
    env.cars[0].speed = env.cars[0].gear_max[0] + 1
    env.step({"throttle": True, "brake": False, "steer": 0.0})
    assert env.cars[0].speed > env.cars[0].gear_max[0]
    assert len(env.track.obstacles) > start_obstacles
