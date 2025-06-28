import os
import pytest

pygame = pytest.importorskip("pygame")

from super_pole_position.envs.pole_position import PolePositionEnv


def test_player_sprite_visible() -> None:
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.display.init()
    env = PolePositionEnv(render_mode="human")
    env.reset(seed=7)
    for _ in range(30):
        env.step(env.action_space.sample())
    env.render()
    surface = env.screen
    assert surface is not None
    w, h = surface.get_size()
    sample = surface.get_at((w // 2, int(h * 0.9)))
    assert sample.r > 150 and sample.g < 50
    pygame.display.quit()
