"""
Arcade HUD drawn with an 8x8 bitmap font.

The font is pre-sliced from ``spritesheet_font.png`` loaded at
runtime. Only blitting operations are used – no TTF rendering.

── Panda3D HUD (grid_leader/hud.py) ──────────────────────────────────
textNode = OnscreenText(text='SCORE', pos=(0.8,0.9), scale=0.05,
                        font=arcadeFont)
...
── Pygame translation ────────────────────────────────────────────────
# Pre-slice 8x8 glyphs into dict; blit per char.  No runtime font render.
"""

from __future__ import annotations

from typing import Dict
import base64
import io
import pathlib
import pygame


class HUD:
    """Pole Position style HUD using bitmap fonts."""

    FONT_W, FONT_H = 8, 8

    _FONT_B64 = (
        """
        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
        zDLrH6j/AIsqdBnfaFCwAAAAAElFTkSuQmCC
        """
    )
    def __init__(self, assets_dir: pathlib.Path) -> None:
        font_path = assets_dir / "spritesheet_font.png"
        if font_path.exists():
            sheet = pygame.image.load(font_path).convert()
        else:
            data = base64.b64decode(self._FONT_B64)
            sheet = pygame.image.load(io.BytesIO(data)).convert()
        self.glyphs = self._slice(sheet)

    # ------------------------------------------------------------------
    def _slice(self, sheet: pygame.Surface) -> Dict[str, pygame.Surface]:
        """Return dictionary of glyph surfaces keyed by character."""

        glyphs: Dict[str, pygame.Surface] = {}
        cols = sheet.get_width() // self.FONT_W
        rows = sheet.get_height() // self.FONT_H
        chars = [chr(i) for i in range(32, 32 + cols * rows)]
        for index, ch in enumerate(chars):
            x = (index % cols) * self.FONT_W
            y = (index // cols) * self.FONT_H
            glyph = sheet.subsurface((x, y, self.FONT_W, self.FONT_H)).copy()
            glyphs[ch] = glyph
        return glyphs

    # ------------------------------------------------------------------
    def draw_text(
        self, surf: pygame.Surface, x: int, y: int, text: str, align: str = "left"
    ) -> None:
        """Blit ``text`` onto ``surf`` using the preloaded glyphs."""

        if align == "right":
            x -= len(text) * self.FONT_W
        for ch in text:
            glyph = self.glyphs.get(ch, None)
            if glyph:
                surf.blit(glyph, (x, y))
            x += self.FONT_W

    # ------------------------------------------------------------------
    def draw_hud(
        self,
        surf: pygame.Surface,
        lap_time: float,
        total_time: float,
        score: int,
        speed_kmh: float,
    ) -> None:
        """Draw scoreboard-style HUD fields."""

        lap_str = f"{lap_time:05.1f}"
        time_str = f"{total_time:03.0f}"
        score_str = f"{score:06d}"
        speed_str = f"{int(speed_kmh):03d}"

        # labels
        self.draw_text(surf, 10, 8, "LAP")
        self.draw_text(surf, 50, 8, lap_str, "right")

        self.draw_text(surf, 10, 18, "TIME")
        self.draw_text(surf, 50, 18, time_str, "right")

        self.draw_text(surf, 200, 8, "SCORE")
        self.draw_text(surf, 246, 8, score_str, "right")

        self.draw_text(surf, 200, 18, "KM/H")
        self.draw_text(surf, 246, 18, speed_str, "right")
