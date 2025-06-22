#!/usr/bin/env python3
"""Generate placeholder PNG sprites for development."""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

try:
    import pygame  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    pygame = None

SPRITE_SPECS = {
    "player_car.png": (32, 32, (200, 0, 0)),
    "cpu_car.png": (32, 32, (0, 0, 200)),
    "mt_fuji.png": (256, 64, (50, 50, 50)),
    "clouds.png": (256, 32, (180, 180, 180)),
    "explosion_16f.png": (32 * 16, 32, (255, 150, 0)),
}
for i in range(1, 9):
    SPRITE_SPECS[f"billboard_{i}.png"] = (32, 32, (0, 150, 0))


def _draw_text(surf: "pygame.Surface", text: str) -> None:
    font = pygame.font.Font(None, 12)
    img = font.render(text, True, (255, 255, 255))
    rect = img.get_rect(center=surf.get_rect().center)
    surf.blit(img, rect)


def generate_sprite(name: str, file: Path) -> None:
    """Create a simple placeholder image for ``name`` at ``file``."""
    if pygame is None:
        return
    spec = SPRITE_SPECS.get(f"{name}.png", (32, 32, (80, 80, 80)))
    width, height, color = spec
    pygame.init()
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    surf.fill(color)
    _draw_text(surf, name.split(".")[0])
    file.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(surf, str(file))
    pygame.quit()


def generate_all(base: Path | None = None) -> None:
    """Generate placeholders for all known sprites under ``base``."""
    if pygame is None:
        return
    base = base or Path(__file__).resolve().parent
    for name in SPRITE_SPECS:
        path = base / name
        if not path.exists() or path.stat().st_size == 0:
            generate_sprite(name[:-4], path)


if __name__ == "__main__":
    generate_all()
