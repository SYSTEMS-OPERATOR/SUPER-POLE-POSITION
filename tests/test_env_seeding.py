from super_pole_position.envs.pole_position import PolePositionEnv


def test_reset_seed_determinism():
    env = PolePositionEnv(render_mode="human")
    obs1, info1 = env.reset(seed=42)
    obs2, info2 = env.reset(seed=42)
    assert info1["track_hash"] == info2["track_hash"]
    assert (obs1 == obs2).all()
    env.close()
