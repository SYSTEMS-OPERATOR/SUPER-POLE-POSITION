import types
import pytest  # noqa: F401

pygame = pytest.importorskip("pygame")
from super_pole_position.ui.arcade import ArcadeRenderer  # noqa: E402


def test_explosion_frame_index(monkeypatch):
    screen = pygame.Surface((32, 32))
    renderer = ArcadeRenderer(screen)
    renderer.explosion_sheet = pygame.Surface((160, 10))

    env = types.SimpleNamespace(crash_duration=1.6, crash_timer=1.6)
    rects = []

    def fake_sub(rect):
        rects.append(rect)
        return pygame.Surface((10, 10))

    renderer.explosion_sheet.subsurface = fake_sub
    renderer.draw_explosion(env, (0, 0))
    assert rects[-1][0] == 0

    env.crash_timer = 0.0
    renderer.draw_explosion(env, (0, 0))
    assert rects[-1][0] == 150
