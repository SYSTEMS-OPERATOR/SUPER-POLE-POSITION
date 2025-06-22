import pygame
import pytest

from super_pole_position.ui.sprites import load_sprite

pygame = pytest.importorskip("pygame")


def test_load_sprite_png(tmp_path, monkeypatch):
    pygame.display.init()
    img = pygame.Surface((4, 4))
    img.fill((255, 0, 0))
    fname = tmp_path / "sample.png"
    pygame.image.save(img, str(fname))
    monkeypatch.setenv("SPRITE_DIR", str(tmp_path))
    surf = load_sprite("sample")
    assert surf.get_size() == (4, 4)
    pygame.display.quit()
