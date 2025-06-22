import pathlib

import pygame

from src.render.background import Background

pygame.display.init()
pygame.display.set_mode((1, 1))


def test_no_bg_flag() -> None:
    bg = Background(pathlib.Path("assets"), no_bg=True)
    surf = pygame.Surface((256, 224))
    bg.draw(surf, player_x=1000, curvature=0.1)
