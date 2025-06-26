import types
import pytest
from src.render.pseudo3d_renderer import Renderer, WIDTH

pygame = pytest.importorskip("pygame")


def _env(steer: float):
    return types.SimpleNamespace(
        cars=[types.SimpleNamespace(speed=0.0, x=0.0)],
        track=types.SimpleNamespace(curvature_at=lambda x: 0.0),
        sprites=[("player_car", 0.1, 0)],
        last_steer=steer,
    )


def test_bank_frame_switch() -> None:
    pygame.display.init()
    pygame.display.set_mode((1, 1))
    env = _env(0.6)
    r = Renderer(None)
    surf_r = pygame.Surface((10, 10))
    surf_r.fill((10, 0, 0))
    surf_l = pygame.Surface((10, 10))
    surf_l.fill((0, 10, 0))
    base = pygame.Surface((10, 10))
    base.fill((0, 0, 10))
    r.sprites = {"player_car_bankR": surf_r, "player_car_bankL": surf_l, "player_car": base}
    r.draw(env)
    color = r.surface.get_at((WIDTH // 2 - 4, 202))[:3]
    assert color[0] > color[1]

    env = _env(-0.6)
    r.draw(env)
    color = r.surface.get_at((WIDTH // 2 - 4, 202))[:3]
    assert color[1] > color[0]
    pygame.display.quit()
