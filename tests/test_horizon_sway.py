import math
import pygame

from super_pole_position.envs.pole_position import PolePositionEnv
from super_pole_position.ui.arcade import Pseudo3DRenderer


def test_horizon_sway_factor():
    pygame.display.init()
    screen = pygame.display.set_mode((320, 240))
    env = PolePositionEnv(render_mode="human")
    env.reset()
    renderer = Pseudo3DRenderer(screen)
    renderer.horizon_sway = 0.2
    env.track.angle_at = lambda x: math.pi / 4
    renderer.draw(env)
    width = renderer.canvas.get_width()
    expected = int(renderer.horizon_base + (width / 4) * renderer.horizon_sway)
    assert renderer.horizon == expected
    pygame.display.quit()
