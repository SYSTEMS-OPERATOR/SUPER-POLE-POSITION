from super_pole_position.envs.pole_position import PolePositionEnv


def test_finish_line_grace():
    env = PolePositionEnv(render_mode="human", mode="race")
    env.reset()
    env.start_timer = 0
    env.cars[0].gear = 1
    env.cars[0].speed = 20.0
    dt = 1.0 / env.metadata.get("render_fps", 60)
    env.remaining_time = dt / 2
    env.cars[0].x = env.track.start_x + env.track.width - 0.5
    env.prev_progress = env.track.progress(env.cars[0])
    obs, _, done, _, _ = env.step((True, False, 0.0))
    assert env.lap >= 1
    assert env.remaining_time > 0
    assert not done
    env.close()
