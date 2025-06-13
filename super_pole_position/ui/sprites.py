#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 MIND INTERFACES, INC. All rights reserved.
# Licensed under the MIT License.

"""
sprites.py
Description: Module for Super Pole Position.
"""


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
    [
        " * ",
        "***",
        " * ",
    ],
    [
        " *** ",
        "*****",
        " *** ",
    ],
    [
        "*****",
        "*****",
        "*****",
    ],
    [
        "  *  ",
        " * * ",
        "  *  ",
    ],
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
