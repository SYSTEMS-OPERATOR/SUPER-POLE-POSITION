from __future__ import annotations

from pathlib import Path

import pygame


class Background:
    """Simple parallax sky and mountain renderer."""

    def __init__(self, assets_dir: Path, no_bg: bool = False) -> None:
        self.no_bg = no_bg
        if no_bg:
            self.mt = None
            self.clouds = None
        else:
            try:
                self.mt = pygame.image.load(assets_dir / "mt_fuji.png").convert()
            except Exception:
                self.mt = None
            try:
                self.clouds = pygame.image.load(assets_dir / "clouds.png").convert_alpha()
            except Exception:
                self.clouds = None

    # ------------------------------------------------------------------
    def draw(self, surface: pygame.Surface, player_x: float, curvature: float) -> None:
        """Draw the sky background relative to ``player_x`` and ``curvature``."""

        if self.no_bg or not pygame:
            return

        if self.clouds:
            w = self.clouds.get_width()
            offset = int((player_x * 0.2) % w)
            for x in (-offset, -offset + w, -offset + 2 * w):
                surface.blit(self.clouds, (x, 20))

        if self.mt:
            bucket = round(curvature, 3)
            shift = {
                -0.02: -24,
                -0.015: -18,
                -0.01: -12,
                -0.005: -6,
                0: 0,
                0.005: 6,
                0.01: 12,
                0.015: 18,
                0.02: 24,
            }.get(bucket, 0)
            mt_w = self.mt.get_width()
            mt_x = 128 - mt_w // 2 + shift
            surface.blit(self.mt, (mt_x, 40))

"""
── Panda3D snippet (grid_leader/sky.py) ───────────────────────────────
clouds.setTexOffset(u, player.x*0.0002)
mt_fuji.setX(curvature*30)

# Pygame translation replicates same offsets by per-frame blit positions.
"""
