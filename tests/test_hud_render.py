import pytest
pygame = pytest.importorskip("pygame")
from super_pole_position.envs.pole_position import PolePositionEnv
from super_pole_position.ui.arcade import Pseudo3DRenderer


def test_hud_render_smoke():
    pygame.display.init()
    screen = pygame.display.set_mode((320, 240))
    env = PolePositionEnv(render_mode="human")
    env.reset()
    renderer = Pseudo3DRenderer(screen)
    renderer.draw(env)
    pygame.display.quit()
