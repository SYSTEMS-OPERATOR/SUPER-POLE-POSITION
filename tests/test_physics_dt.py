from super_pole_position.envs.pole_position import PolePositionEnv


class DummyClock:
    def __init__(self, ms):
        self.ms = ms

    def get_time(self):
        return self.ms


def test_step_uses_clock_dt():
    env = PolePositionEnv(render_mode="human")
    env.clock = DummyClock(500)  # 0.5s
    env.reset()
    prev = env.cars[0].speed
    env.step((True, False, 0.0))
    assert env.cars[0].speed > prev
    env.close()

