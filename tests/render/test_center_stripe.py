import types
import pytest
pygame = pytest.importorskip("pygame")
from src.render.pseudo3d_renderer import Renderer, WIDTH, HEIGHT


def test_center_stripe_drawn() -> None:
    pygame.display.init()
    pygame.display.set_mode((1, 1))
    env = types.SimpleNamespace(
        cars=[types.SimpleNamespace(speed=100.0, x=0.0)],
        track=types.SimpleNamespace(curvature_at=lambda x: 0.0),
        sprites=[],
    )
    r = Renderer(None)
    r.draw(env)
    color = r.surface.get_at((WIDTH // 2, HEIGHT - 2))[:3]
    assert color != (60, 60, 60)
    pygame.display.quit()
