import pytest
from super_pole_position.ui import sprites

pygame = pytest.importorskip("pygame")


def test_player_car_min_size() -> None:
    pygame.display.init()
    surf = sprites.load_sprite("player_car", sprites.CAR_ART)
    assert surf.get_width() >= 32
    assert surf.get_height() >= 32
    pygame.display.quit()
