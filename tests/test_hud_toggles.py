import os
import types
import pytest
pygame = pytest.importorskip("pygame")  # noqa: E402
from super_pole_position.ui.arcade import Pseudo3DRenderer  # noqa: E402


def test_hud_gear_toggle(monkeypatch):
    pygame.display.init()
    pygame.font.init()
    screen = pygame.display.set_mode((160, 120))
    monkeypatch.setenv("HUD_GEAR", "0")
    renderer = Pseudo3DRenderer(screen)
    assert not renderer.show_gear
    env = types.SimpleNamespace(
        mode="race",
        cars=[types.SimpleNamespace(speed=0, gear=0, x=0, y=0)],
        traffic=[],
        track=types.SimpleNamespace(width=100, height=100, start_x=0,
                                    distance=lambda a,b: 10,
                                    angle_at=lambda x: 0),
        remaining_time=0.0,
        lap_timer=None,
        lap_flash=0.0,
        last_lap_time=None,
        lap=0,
        start_phase="",
        message_timer=0,
        game_message="",
        current_step=0,
        time_extend_flash=0,
    )
    texts = []
    class DummyFont:
        def render(self, text, aa, color):
            texts.append(text)
            return pygame.Surface((1, 1))
    monkeypatch.setattr(pygame.font, "SysFont", lambda *a, **k: DummyFont())
    renderer.draw(env)
    assert all("GEAR" not in t for t in texts)
    pygame.display.quit()


def test_hud_minimap_toggle(monkeypatch):
    pygame.display.init()
    pygame.font.init()
    screen = pygame.display.set_mode((160, 120))
    monkeypatch.setenv("HUD_MINIMAP", "0")
    renderer = Pseudo3DRenderer(screen)
    assert not renderer.show_minimap
    pygame.display.quit()
