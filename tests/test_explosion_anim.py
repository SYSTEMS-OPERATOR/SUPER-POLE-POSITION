import types
import pytest
pygame = pytest.importorskip("pygame")  # noqa: E402
from super_pole_position.ui.arcade import ArcadeRenderer  # noqa: E402


def test_explosion_frame_indices():
    pygame.display.init()
    pygame.font.init()
    screen = pygame.display.set_mode((64, 64))
    import os
    os.environ["AUDIO"] = "0"
    renderer = ArcadeRenderer(screen)
    renderer.explosion_sheet = pygame.Surface((160, 10))
    env = types.SimpleNamespace(crash_duration=2.56, crash_timer=2.56)
    indices = []
    for i in range(16):
        env.crash_timer = env.crash_duration - i * (env.crash_duration / 16) - 0.01
        idx = renderer.draw_explosion(env, (0, 0))
        indices.append(idx)
    assert indices == list(range(16))
    pygame.display.quit()
