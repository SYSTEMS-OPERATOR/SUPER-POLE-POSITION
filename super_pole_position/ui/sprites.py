#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 MIND INTERFACES, INC. All rights reserved.
# Licensed under the MIT License.

"""
sprites.py
Description: Module for Super Pole Position.
"""

import os
from pathlib import Path
import importlib.util

# Hide pygame's greeting for cleaner logs
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")



try:
    import pygame  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    pygame = None


# --- ASCII sprite definitions -----------------------------------------------

CAR_ART = [
    " rrr ",
    "rrrrr",
    " rrr ",
]

BILLBOARD_ART = [
    "#####",
    "#F F#",
    "#F F#",
    "#####",
]

EXPLOSION_FRAMES = [
    [" * ", "***", " * "],
    [" *** ", "*****", " *** "],
    ["*****", "*****", "*****"],
    ["  *  ", " * * ", "  *  "],
    ["  **  ", " **** ", "  **  "],
    [" **** ", "******", " **** "],
    ["******", "******", "******"],
    ["   *   ", "  * *  ", "   *   "],
]


_COLOR_MAP = {
    "r": (255, 0, 0),
    "F": (255, 255, 255),
    "#": (255, 255, 255),
    "*": (255, 200, 0),
}


def ascii_surface(ascii_art: list[str], scale: int = 1) -> "pygame.Surface | None":
    """Return a pygame surface from ASCII art or ``None`` if pygame missing."""
    if not pygame:
        return None
    if not ascii_art:
        return pygame.Surface((1, 1), pygame.SRCALPHA)
    height = len(ascii_art)
    width = max(len(line) for line in ascii_art)
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    for y, line in enumerate(ascii_art):
        for x, ch in enumerate(line):
            if ch != " ":
                color = _COLOR_MAP.get(ch, (255, 255, 255))
                surf.set_at((x, y), color)
    if scale > 1:
        surf = pygame.transform.scale(surf, (width * scale, height * scale))
    return surf


def load_sprite(name: str, ascii_art: list[str] | None = None) -> "pygame.Surface | None":
    """Return a sprite loaded from ``assets/sprites`` or fallback to ASCII.

    Parameters
    ----------
    name:
        File name without extension.
    ascii_art:
        Optional ASCII art fallback.
    """

    if not pygame:
        return ascii_surface(ascii_art or [])
    base = os.getenv("SPRITE_DIR")
    if base:
        path = Path(base) / f"{name}.png"
    else:
        path = Path(__file__).resolve().parents[2] / "assets" / "sprites" / f"{name}.png"

    if not path.exists() or path.stat().st_size == 0:
        gen_path = Path(__file__).resolve().parents[2] / "assets" / "sprites" / "generate_placeholders.py"
        if gen_path.exists() and not pygame.display.get_init():
            spec = importlib.util.spec_from_file_location("generate_placeholders", gen_path)
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                try:
                    mod.generate_sprite(name, path)
                except Exception:
                    pass

    surf: "pygame.Surface | None" = None
    if path.exists() and path.stat().st_size > 0:
        try:
            surf = pygame.image.load(str(path)).convert_alpha()
        except Exception:
            surf = None
    else:
        gen = path.parent / "generate_placeholders.py"
        if gen.exists() and not pygame.display.get_init():
            try:
                spec = importlib.util.spec_from_file_location("placeholder_gen", gen)
                if spec and spec.loader:
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    if hasattr(mod, "generate_all"):
                        mod.generate_all(path.parent)
                    elif hasattr(mod, "generate_sprite"):
                        size_map: dict[str, tuple[int, int]] = getattr(
                            mod, "_parse_sprite_specs", lambda _: {}
                        )(path.parent / "SPRITES.md")
                        mod.generate_sprite(name, path, size_map)
            except Exception:
                pass
            if path.exists() and path.stat().st_size > 0:
                try:
                    surf = pygame.image.load(str(path)).convert_alpha()
                except Exception:
                    surf = None
    if surf is None:
        surf = ascii_surface(ascii_art or [])
        if surf is None:
            return None
    w, h = surf.get_size()
    if w < 32 or h < 32:
        padded = pygame.Surface((32, 32), pygame.SRCALPHA)
        padded.blit(surf, ((32 - w) // 2, (32 - h) // 2))
        surf = padded
    return surf
