#!/usr/bin/env python3
"""Generate placeholder PNG sprites for development."""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Dict, Tuple

# Hide pygame greeting and use dummy video driver for headless generation
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

try:
    import pygame
except Exception:  # pragma: no cover - optional dependency
    pygame = None

DEFAULT_COLOR = (128, 128, 128)
COLOR_MAP: Dict[str, Tuple[int, int, int]] = {
    "player_car.png": (200, 0, 0),
    "cpu_car.png": (0, 0, 200),
    "explosion_16f.png": (255, 150, 0),
    "mt_fuji.png": (50, 50, 50),
    "clouds.png": (180, 180, 180),
}


def _parse_sprite_specs(md_file: Path) -> Dict[str, Tuple[int, int]]:
    """Return mapping of sprite filename to (width, height)."""

    pattern = re.compile(r"`([^`]+)`.*?Size (\d+)×(\d+)")
    specs: Dict[str, Tuple[int, int]] = {}
    if not md_file.exists():
        return specs
    for line in md_file.read_text().splitlines():
        match = pattern.search(line)
        if match:
            name = match.group(1)
            specs[name] = (int(match.group(2)), int(match.group(3)))
    return specs


def _write_sprite(path: Path, size: Tuple[int, int], color: Tuple[int, int, int], text: str) -> None:
    if pygame is None:
        return
    surf = pygame.Surface(size)
    surf.fill(color)
    font = pygame.font.Font(None, 12)
    label = font.render(text, True, (255, 255, 255))
    rect = label.get_rect(center=(size[0] // 2, size[1] // 2))
    surf.blit(label, rect)
    path.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(surf, str(path))


def generate_sprite(name: str, path: Path, size_map: Dict[str, Tuple[int, int]]) -> None:
    """Create a placeholder image for ``name`` if missing."""

    if pygame is None:
        return
    if path.exists() and path.stat().st_size > 0:
        return

    size = size_map.get(name + ".png", (32, 32))
    color = DEFAULT_COLOR
    for key, value in COLOR_MAP.items():
        if name + ".png" == key or key.startswith("billboard") and name.startswith("billboard"):
            color = value
            break

    _write_sprite(path, size, color, name)


def generate_all(base: Path | None = None) -> None:
    """Generate placeholders for all sprites listed in SPRITES.md."""

    if pygame is None:
        return
    base = base or Path(__file__).resolve().parent
    specs = _parse_sprite_specs(base / "SPRITES.md")

    pygame.init()
    for name in specs:
        out = base / name
        generate_sprite(name[:-4], out, specs)
    pygame.quit()


if __name__ == "__main__":
    generate_all()
