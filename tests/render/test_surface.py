import pytest

pygame = pytest.importorskip("pygame")

from src.render.pseudo3d_renderer import Renderer  # noqa: E402

def test_surface_size():
    r = Renderer(None)
    assert r.surface.get_width() == 256 and r.surface.get_height() == 224
