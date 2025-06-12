import pygame
from super_pole_position.ui.sprites import ascii_surface, CAR_ART


def test_ascii_surface():
    pygame.display.init()
    surf = ascii_surface(CAR_ART)
    assert surf is not None
    assert surf.get_width() == len(CAR_ART[0])
    pygame.display.quit()
