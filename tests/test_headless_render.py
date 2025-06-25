import os
import pygame
from super_pole_position.ui.arcade import Pseudo3DRenderer
from super_pole_position.envs.pole_position import PolePositionEnv


def test_headless_render_smoke():
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.display.init()
    screen = pygame.display.set_mode((256, 224))
    renderer = Pseudo3DRenderer(screen)
    env = PolePositionEnv(render_mode="human")
    env.reset(seed=0)
    renderer.draw(env)
    pygame.display.quit()
    env.close()
