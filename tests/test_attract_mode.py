import pytest
from super_pole_position.ui import menu

pygame = pytest.importorskip('pygame')


def test_attract_mode_cycles_scores(monkeypatch):
    calls = []

    def fake_show(screen, font):
        calls.append(True)

    monkeypatch.setattr(menu, "_show_high_scores", fake_show)
    pygame.init()
    screen = pygame.display.set_mode((320, 240))
    monkeypatch.setenv("ATTRACT_MODE", "1")
    monkeypatch.setenv("FAST_TEST", "1")
    menu.main_loop(screen, seed=42)
    pygame.quit()
    assert calls
