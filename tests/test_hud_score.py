import types
import pytest
pygame = pytest.importorskip("pygame")  # noqa: E402
from super_pole_position.ui.arcade import ArcadeRenderer  # noqa: E402


def test_hud_high_score_updates(monkeypatch):
    pygame.display.init()
    pygame.font.init()
    screen = pygame.display.set_mode((160, 120))
    import os
    os.environ["AUDIO"] = "0"
    renderer = ArcadeRenderer(screen)
    env = types.SimpleNamespace(
        score=123,
        high_score=100,
        cars=[types.SimpleNamespace(speed=0, gear=0)],
        remaining_time=0.0,
        lap_timer=None,
        lap_flash=0.0,
        last_lap_time=None,
    )
    class DummyFont:
        def __init__(self):
            self.texts = []

        def render(self, text, aa, color):
            self.texts.append(text)
            return pygame.Surface((1, 1))

    renderer.font = DummyFont()
    renderer.draw_hud(env)
    assert env.high_score == 123
    assert any("SCORE 00123" in t and "HI 00123" in t for t in renderer.font.texts)
    pygame.display.quit()
