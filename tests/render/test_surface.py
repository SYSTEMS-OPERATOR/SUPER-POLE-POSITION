import pytest
from src.render.pseudo3d_renderer import Renderer

pygame = pytest.importorskip("pygame")

def test_surface_size():
    r = Renderer(None)
    assert r.surface.get_width() == 256 and r.surface.get_height() == 224
