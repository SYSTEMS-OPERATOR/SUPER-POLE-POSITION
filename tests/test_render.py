import types
import math
import pytest
pygame = pytest.importorskip("pygame")  # noqa: E402
from super_pole_position.ui.arcade import Pseudo3DRenderer  # noqa: E402


def test_draw_road_polygon_offset():
    pygame.display.init()
    screen = pygame.display.set_mode((320, 240))
    renderer = Pseudo3DRenderer(screen)
    env = types.SimpleNamespace(
        cars=[types.SimpleNamespace(angle=0.0, steering=0.5, x=0.0)],
        track=types.SimpleNamespace(angle_at=lambda x: math.pi / 8),
        last_steer=0.5,
    )
    poly = renderer.draw_road_polygon(env)
    width = renderer.canvas.get_width()
    road_top = width * 0.6 * 0.2
    expected = 0.5 * (width / 4) + 0.5 * 0.12 * width
    assert poly[2][0] == pytest.approx(width / 2 + expected + road_top / 2)
    assert poly[3][0] == pytest.approx(width / 2 + expected - road_top / 2)
    pygame.display.quit()


def test_ground_color_green() -> None:
    pygame.display.init()
    screen = pygame.display.set_mode((320, 240))
    renderer = Pseudo3DRenderer(screen)
    assert renderer.ground_color == (0, 184, 0)
    pygame.display.quit()
