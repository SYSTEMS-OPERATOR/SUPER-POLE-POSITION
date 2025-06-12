from super_pole_position.envs.pole_position import PolePositionEnv


def test_prepare_voice_on_reset():
    env = PolePositionEnv(render_mode="human")
    env.reset()
    assert env.start_phase == "READY"
