import numpy as np
from super_pole_position.envs.pole_position import PolePositionEnv


def collect_obs(seed: int) -> tuple[str, bytes]:
    env = PolePositionEnv(render_mode="human", seed=seed)
    obs, info = env.reset(seed=seed)
    buf = bytearray(obs.tobytes())
    for _ in range(200):
        obs, *_ = env.step({"throttle": 0.5, "brake": 0.0, "steer": 0.0})
        buf.extend(obs.tobytes())
    env.close()
    return info.get("track_hash", ""), bytes(buf)


def test_determinism_seeded():
    h1, o1 = collect_obs(42)
    h2, o2 = collect_obs(42)
    assert h1 == h2
    assert o1 == o2

