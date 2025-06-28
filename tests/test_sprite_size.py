import pytest

pygame = pytest.importorskip("pygame")

from super_pole_position.ui import sprites


def test_player_sprite_size() -> None:
    pygame.display.init()
    surf = sprites.load_sprite("player_car", ascii_art=sprites.CAR_ART)
    assert surf.get_width() >= 32 and surf.get_height() >= 32
    pygame.display.quit()
