from super_pole_position.envs.pole_position import PolePositionEnv


def test_lap_timer_resets():
    env = PolePositionEnv(render_mode="human", mode="race")
    env.reset()
    env.start_timer = 0
    env.cars[0].gear = 1
    env.cars[0].x = env.track.start_x + env.track.width - 1
    env.step((False, False, 0.0))
    env.cars[0].x = env.track.start_x + env.track.width + 1
    env.step((False, False, 0.0))
    assert env.last_lap_time is not None
    assert env.lap_timer == 0.0
    env.close()
