"""
Pixel-perfect pseudo 3D renderer.

── Panda3D road shader (grid_leader/shaders/road.glsl) ───────────────
for (int i=0;i<64;i++){
    float depth = i/64.0;
    float scale = pow(1.0-depth,2.0);
    float curve = sampleCurvature(depth);
    float halfwidth = scale*(1.0+curve*i);
    vec2 a = vec2(cx-halfwidth, y);
    vec2 b = vec2(cx+halfwidth, y);
    drawQuad(a,b,...);
}

── Pygame translation guideline ──────────────────────────────────────
# Pygame lacks shaders; draw 64 trapezoid quads in Python loop.
# Derive same 'halfwidth' & 'curve' math; pre-compute lists for speed.
"""

from __future__ import annotations

from typing import Iterable, List, Tuple

import pygame

WIDTH = 256
HEIGHT = 224
BASE_ROAD_HALF = 77.0
ROAD_GRAY = (60, 60, 60)
HORIZON_GAIN = 120


class Renderer:
    """Pseudo-3D road renderer using pygame."""

    def __init__(self, display: pygame.Surface | None) -> None:
        self.display = display
        self.surface = pygame.Surface((WIDTH, HEIGHT))
        self.scanline = pygame.Surface((WIDTH, 2), pygame.SRCALPHA)
        self.scanline.fill((0, 0, 0, 38))
        self.horizon = 90
        self.sprites: dict[str, pygame.Surface] = {}

    # ------------------------------------------------------------------
    def perspective_scale(self, depth: float) -> float:
        """Return scale factor for given depth (0..1)."""

        depth = max(0.0, min(depth, 1.0))
        return (1.0 - depth) ** 2

    # ------------------------------------------------------------------
    def depth_to_y(self, depth: float) -> float:
        """Return y coordinate at ``depth``."""

        bottom = HEIGHT
        return bottom - (bottom - self.horizon) * depth

    # ------------------------------------------------------------------
    def draw(self, env) -> None:
        """Draw the environment to ``self.surface``."""

        if pygame is None:
            return
        player = env.cars[0]
        base_x = WIDTH // 2
        bottom = HEIGHT
        road_half_prev = BASE_ROAD_HALF
        cx_prev = base_x
        y_prev = bottom
        for i in range(64):
            depth_prev = i / 64.0
            depth = (i + 1) / 64.0
            curv_prev = env.track.curvature_at(player.x + depth_prev * 100)
            curv = env.track.curvature_at(player.x + depth * 100)
            scale_prev = self.perspective_scale(depth_prev)
            scale = self.perspective_scale(depth)
            road_half_curr = scale * (1 + curv * (i + 1)) * BASE_ROAD_HALF
            road_half_prev = scale_prev * (1 + curv_prev * i) * BASE_ROAD_HALF
            y = self.depth_to_y(depth)
            y_prev = self.depth_to_y(depth_prev)
            cx = base_x + sum(
                env.track.curvature_at(player.x + d * 100) * (d ** 2)
                for d in (0.0, depth)
            ) * HORIZON_GAIN
            cx_prev = base_x + sum(
                env.track.curvature_at(player.x + d * 100) * (d ** 2)
                for d in (0.0, depth_prev)
            ) * HORIZON_GAIN
            pygame.draw.polygon(
                self.surface,
                ROAD_GRAY,
                [
                    (cx_prev - road_half_prev, y_prev),
                    (cx_prev + road_half_prev, y_prev),
                    (cx + road_half_curr, y),
                    (cx - road_half_curr, y),
                ],
            )
            stripe_color = (255, 0, 0) if (i // 4) % 2 == 0 else (255, 255, 255)
            pygame.draw.polygon(
                self.surface,
                stripe_color,
                [
                    (cx_prev - road_half_prev - 6, y_prev),
                    (cx_prev - road_half_prev, y_prev),
                    (cx - road_half_curr, y),
                    (cx - road_half_curr - 6, y),
                ],
            )
            pygame.draw.polygon(
                self.surface,
                stripe_color,
                [
                    (cx_prev + road_half_prev, y_prev),
                    (cx_prev + road_half_prev + 6, y_prev),
                    (cx + road_half_curr + 6, y),
                    (cx + road_half_curr, y),
                ],
            )

        sprites = getattr(env, "sprites", [])
        sprites_sorted = sorted(sprites, key=lambda s: s[1], reverse=True)
        for name, depth, lateral in sprites_sorted:
            img = self.sprites.get(name)
            if not img:
                continue
            scale = self.perspective_scale(depth)
            w, h = img.get_size()
            img_scaled = pygame.transform.scale(
                img, (int(w * scale), int(h * scale))
            )
            cx = base_x + sum(
                env.track.curvature_at(player.x + d * 100) * (d ** 2)
                for d in (0.0, depth)
            ) * HORIZON_GAIN
            slice_y = self.depth_to_y(depth)
            screen_x = int(cx + lateral - img_scaled.get_width() // 2)
            screen_y = int(slice_y - img_scaled.get_height())
            self.surface.blit(img_scaled, (screen_x, screen_y))

        for y in range(0, HEIGHT, 2):
            self.surface.blit(self.scanline, (0, y))

        if self.display:
            if (
                self.display.get_width() != WIDTH
                or self.display.get_height() != HEIGHT
            ):
                scaled = pygame.transform.scale(
                    self.surface, self.display.get_size()
                )
                self.display.blit(scaled, (0, 0))
            else:
                self.display.blit(self.surface, (0, 0))

