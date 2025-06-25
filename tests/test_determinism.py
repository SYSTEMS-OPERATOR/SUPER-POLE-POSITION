import numpy as np
from super_pole_position.envs.pole_position import PolePositionEnv


def collect_obs(seed: int, steps: int = 200):
    env = PolePositionEnv(render_mode="human", seed=seed)
    obs, info = env.reset(seed=seed)
    steps = min(steps, env.max_steps)
    data = [obs.tobytes()]
    for _ in range(steps):
        obs, *_ = env.step({"throttle": False, "brake": False, "steer": 0.0})
        data.append(obs.tobytes())
    env.close()
    return info["track_hash"], b"".join(data)


def test_determinism_seeded():
    h1, d1 = collect_obs(123)
    h2, d2 = collect_obs(123)
    assert h1 == h2
    assert d1 == d2
