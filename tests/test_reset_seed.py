from super_pole_position.envs.pole_position import PolePositionEnv


def test_reset_seed_determinism():
    env = PolePositionEnv(render_mode="human", seed=42)
    obs1, info1 = env.reset(seed=42)
    obs2, info2 = env.reset(seed=42)
    assert info1["track_hash"] == info2["track_hash"]
    assert obs1.tobytes() == obs2.tobytes()
    env.close()
