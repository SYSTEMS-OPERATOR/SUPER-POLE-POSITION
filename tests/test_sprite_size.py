import pytest
from super_pole_position.ui.sprites import load_sprite

pygame = pytest.importorskip("pygame")


def test_player_sprite_size() -> None:
    pygame.display.init()
    surf = load_sprite("player_car")
    assert surf.get_width() >= 32 and surf.get_height() >= 32
    pygame.display.quit()
