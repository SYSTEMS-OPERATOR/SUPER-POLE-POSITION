import pygame
import pytest
from src.render.pseudo3d_renderer import Renderer

pygame = pytest.importorskip("pygame")


def test_sprite_alpha_reduces_near_horizon() -> None:
    surf = pygame.Surface((4, 4))
    surf.fill((255, 255, 255))
    r = Renderer(None)
    faded = r._apply_horizon_fade(surf, 60 / 63)
    alpha = faded.get_alpha() or 255
    assert alpha < 90
