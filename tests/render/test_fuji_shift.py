import pytest
from pathlib import Path
from src.render.background import Background

pygame = pytest.importorskip("pygame")


def test_fuji_shift_lut() -> None:
    bg = Background(Path("assets"))
    surf = pygame.Surface((256, 224))
    bg.draw(surf, player_x=0, curvature=0.02)
    if bg.mt:
        expected = 128 - bg.mt.get_width() // 2 + 24
        color = surf.get_at((expected + 1, 41))[:3]
        assert color != (0, 0, 0)
