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
    # slice 0 should show a bright stripe
    color = r.surface.get_at((WIDTH // 2, HEIGHT - 2))[:3]
    assert color[0] >= 210
    # near the horizon no stripe should be drawn
    top_y = int(r.depth_to_y(63 / 64))
    top_color = r.surface.get_at((WIDTH // 2, top_y))[:3]
    assert top_color[0] < 200
    pygame.display.quit()
