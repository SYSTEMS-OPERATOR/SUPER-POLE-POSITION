import os
import pytest

pygame = pytest.importorskip("pygame")

from src.render.pseudo3d_renderer import Renderer  # noqa: E402


def test_headless_render_smoke():
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.display.init()
    screen = pygame.display.set_mode((256, 224))
    renderer = Renderer(screen)
    renderer.display.fill((0, 0, 0))
    pygame.display.flip()
    pygame.display.quit()
