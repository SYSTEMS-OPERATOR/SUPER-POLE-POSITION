import hashlib
import pathlib
import pytest

pygame = pytest.importorskip("pygame")

from src.ui.hud import HUD  # noqa: E402


def test_digits_checksum() -> None:
    pygame.display.init()
    pygame.display.set_mode((1, 1))
    hud = HUD(pathlib.Path("assets"))
    surf = pygame.Surface((64, 8))
    hud.draw_text(surf, 0, 0, "0123456789")
    buf = pygame.image.tostring(surf, "RGB")
    md5 = hashlib.md5(buf).hexdigest()
    assert md5 == "88c75796612a39012c52f088bd003211"
    pygame.display.quit()
