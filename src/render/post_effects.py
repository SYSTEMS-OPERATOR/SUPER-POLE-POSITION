from __future__ import annotations

import pygame


def bloom(src: pygame.Surface, strength: float = 0.3) -> pygame.Surface:
    """Return ``src`` with a simple bloom effect applied."""

    if strength <= 0 or not pygame:
        return src
    w, h = src.get_size()
    bright = src.copy()
    pygame.transform.threshold(bright, src, (200, 200, 200), (55, 55, 55), (255, 255, 255), 1)
    blur = pygame.transform.smoothscale(bright, (max(1, w // 3), max(1, h // 3)))
    blur = pygame.transform.smoothscale(blur, (w, h))
    blur.set_alpha(int(255 * strength))
    out = src.copy()
    out.blit(blur, (0, 0), special_flags=pygame.BLEND_ADD)
    return out


