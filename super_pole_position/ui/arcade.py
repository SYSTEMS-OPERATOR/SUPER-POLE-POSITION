#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 MIND INTERFACES, INC. All rights reserved.
# Licensed under the MIT License.

"""
arcade.py
Description: Module for Super Pole Position.
"""



import os
from pathlib import Path
from typing import Dict


def _load_config() -> dict:
    """Return arcade parity config from ``config.arcade_parity.yaml``.

    Falls back to defaults when the file is missing or unreadable. A very
    small built-in parser handles ``key: value`` pairs to avoid external
    YAML dependencies.
    """

    default = {"scanline_spacing": 2, "scanline_alpha": 40}
    cfg_path = Path(__file__).resolve().parents[1] / "config.arcade_parity.yaml"
    if not cfg_path.exists():
        return default
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(cfg_path.read_text())
        if isinstance(data, dict):
            default.update(data)
        return default
    except Exception:
        try:
            for line in cfg_path.read_text().splitlines():
                if ":" in line:
                    key, val = line.split(":", 1)
                    val = val.strip().strip("'\"")
                    if val.replace(".", "", 1).isdigit():
                        if "." in val:
                            val = float(val)
                        else:
                            val = int(val)
                    default[key.strip()] = val
        except Exception:
            pass
        return default


_PARITY_CFG = _load_config()
SCANLINE_SPACING = int(_PARITY_CFG.get("scanline_spacing", 2))
SCANLINE_ALPHA = int(_PARITY_CFG.get("scanline_alpha", 40))

from .sprites import BILLBOARD_ART, CAR_ART, EXPLOSION_FRAMES, ascii_surface
from ..evaluation.scores import load_scores

try:
    HIGH_SCORE = max((s["score"] for s in load_scores(None)), default=0)
except Exception:  # pragma: no cover - file may be missing
    HIGH_SCORE = 0

try:
    import pygame  # type: ignore
except Exception:  # pragma: no cover
    pygame = None


def _load_arcade_config() -> Dict[str, int]:
    """Return scanline configuration from ``config.arcade_parity.yaml``."""

    cfg = {"scanline_step": 2, "scanline_alpha": 255}
    path = Path(__file__).resolve().parents[2] / "config.arcade_parity.yaml"
    try:
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                if ":" not in line:
                    continue
                key, val = line.split(":", 1)
                try:
                    cfg[key.strip()] = int(val.strip())
                except Exception:
                    # Ignore non-numeric values and keep defaults
                    continue
    except Exception:
        pass
    return cfg


class Palette:
    """Arcade cabinet palette with basic NTSC gamma approximation."""

    black = (0, 0, 0)
    green = (0, 255, 0)
    white = (255, 255, 255)


def available() -> bool:
    """Return ``True`` if pygame is installed."""

    return pygame is not None


class ArcadeRenderer:
    """Draw HUD and scenery layers using pygame."""

    def __init__(self, screen):
        """Create a renderer bound to ``screen``."""

        self.screen = screen
        self.font = pygame.font.SysFont(None, 24) if pygame else None
        self.palette = {"white": Palette.white}
        self.scenery = []
        if pygame:
            sc_dir = Path(__file__).resolve().parent.parent / "assets" / "scenery"
            for img in sc_dir.glob("*.png"):
                try:
                    self.scenery.append(pygame.image.load(str(img)))
                except Exception:
                    pass
        if pygame and os.environ.get("AUDIO", "1") != "0":
            pygame.mixer.init()
            self.channels = [pygame.mixer.Channel(i) for i in range(3)]
            silent = pygame.mixer.Sound(buffer=b"\0\0")
            self.engine_sound = silent
            self.skid_sound = silent
            crash_path = (
                Path(__file__).resolve().parent.parent
                / "assets"
                / "audio"
                / "crash.wav"
            )
            try:
                # ``crash.wav`` is not included in this repository. A silent
                # placeholder sound avoids load errors during tests.
                self.crash_sound = pygame.mixer.Sound(str(crash_path))
            except Exception:  # pragma: no cover - missing audio
                self.crash_sound = silent
        else:
            self.channels = []
        self.explosion_sheet = None
        if pygame:
            exp_path = (
                Path(__file__).resolve().parent.parent / "assets" / "explosion_16f.png"
            )
            try:
                # Sprite sheet not bundled; will be added later.
                self.explosion_sheet = pygame.image.load(str(exp_path))
            except Exception:
                self.explosion_sheet = None

    def draw_explosion(self, env, pos) -> int:
        """Blit the correct explosion frame at ``pos`` and return its index."""

        if not pygame or not self.explosion_sheet or env.crash_timer <= 0:
            return -1
        frame_width = self.explosion_sheet.get_width() // 16
        frame_height = self.explosion_sheet.get_height()
        duration = getattr(env, "crash_duration", 2.5)
        frame_duration = duration / 16
        frame_index = min(15, int((duration - env.crash_timer) / frame_duration))
        frame_surface = self.explosion_sheet.subsurface(
            (frame_index * frame_width, 0, frame_width, frame_height)
        )
        self.screen.blit(frame_surface, pos)
        return frame_index

    def draw_hud(self, env) -> None:
        """Render HUD elements including score."""

        if not self.font:
            return
        if env.score > getattr(env, "high_score", 0):
            env.high_score = env.score
        score_text = f"SCORE {int(env.score):05d}  HI {int(getattr(env, 'high_score', 0)):05d}"
        self.screen.blit(
            self.font.render(score_text, True, self.palette["white"]),
            (10, 10),
        )
        speed = int(env.cars[0].speed * 2.23694)
        gear = "H" if env.cars[0].gear else "L"
        text = self.font.render(f"SPEED {speed} MPH", True, (255, 255, 255))
        gear_text = self.font.render(f"GEAR {gear}", True, (255, 255, 255))
        self.screen.blit(text, (10, 30))
        self.screen.blit(gear_text, (10, 50))
        time_text = self.font.render(f"TIME {env.remaining_time:05.2f}", True, (255, 255, 0))
        self.screen.blit(time_text, (10, 70))
        lap_val = env.lap_timer if env.lap_flash <= 0 else env.last_lap_time
        if lap_val is not None:
            lap_time = self.font.render(f"LAP {lap_val:05.2f}", True, (0, 255, 0))
            self.screen.blit(lap_time, (10, 90))

    def draw(self, env) -> None:
        """Render the current environment state."""

        if not pygame:
            return
        # parallax scenery
        for i, img in enumerate(self.scenery):
            factor = 1.0 / (i + 1)
            x = int(-env.cars[0].x * factor) % env.screen.get_width()
            self.screen.blit(img, (x, 0))

        # HUD
        self.draw_hud(env)

        # audio channels
        if hasattr(self, "channels"):
            self.channels[0].play(self.engine_sound, loops=-1)
            if getattr(env, "skid_timer", 0) > 0 and not self.channels[1].get_busy():
                self.channels[1].play(self.skid_sound)
            if env.crash_timer > 0 and not self.channels[2].get_busy():
                self.channels[2].play(self.crash_sound)


class Pseudo3DRenderer:
    """Renderer that simulates a pseudo-3D road with sprite scaling.

    The projection is a very rough approximation of the arcade original.
    Objects are drawn with a simple 1/z perspective relative to the player's car
    along the x-axis.  The road converges toward a vanishing point on the
    horizon using linear interpolation.  The horizon shifts based on the
    player's steering angle to mimic curves.
    """

    def __init__(self, screen):
        """Create the renderer bound to ``screen``."""

        self.screen = screen
        if pygame and not pygame.font.get_init():
            pygame.font.init()
        self.horizon_base = int(screen.get_height() * 0.4)
        self.horizon = self.horizon_base
        self.sky_color = (100, 150, 255)
        self.ground_color = (40, 40, 40)
        self.car_color = (255, 0, 0)
        self.car_sprite = ascii_surface(CAR_ART)
        self.billboard_sprite = ascii_surface(BILLBOARD_ART)
        self.explosion_frames = [ascii_surface(f) for f in EXPLOSION_FRAMES]
        self.scanline_spacing = SCANLINE_SPACING
        self.scanline_alpha = SCANLINE_ALPHA

        cfg = _load_arcade_config()
        self.scanline_step = cfg["scanline_step"]
        self.scanline_alpha = cfg["scanline_alpha"]
        if pygame:
            self._scanline_row = pygame.Surface((1, 1), pygame.SRCALPHA)
            self._scanline_row.fill((0, 0, 0, self.scanline_alpha))
        else:
            self._scanline_row = None


    def road_polygon(self, offset: float) -> list[tuple[float, float]]:
        """Return trapezoid points for the road given ``offset``."""

        width = self.screen.get_width()
        height = self.screen.get_height()
        road_w = width * 0.6
        road_top = road_w * 0.2
        return [
            (width / 2 - road_w / 2, height),
            (width / 2 + road_w / 2, height),
            (width / 2 + offset + road_top / 2, self.horizon),
            (width / 2 + offset - road_top / 2, self.horizon),
        ]

    def draw_road_polygon(self, env) -> list[tuple[float, float]]:
        """Draw the road trapezoid and return its points."""

        curvature = getattr(env.cars[0], "steering", env.cars[0].angle)
        curvature = max(-1.0, min(curvature, 1.0))
        offset = curvature * (self.screen.get_width() / 4)
        points = self.road_polygon(offset)
        if pygame:
            pygame.draw.polygon(self.screen, (60, 60, 60), points)
        return points

    def draw(self, env) -> None:
        """Draw the environment from a front-facing perspective."""

        if not pygame:
            return

        width = self.screen.get_width()
        height = self.screen.get_height()

        # sky gradient
        self.screen.fill(self.sky_color)
        pygame.draw.rect(
            self.screen,
            self.ground_color,
            (0, self.horizon, width, height - self.horizon),
        )

        # road trapezoid (vanishing point shifts with curvature)
        road_w = width * 0.6
        bottom = height
        player = env.cars[0]
        curvature = getattr(player, "steering", player.angle)
        curvature = max(-1.0, min(curvature, 1.0))
        offset = curvature * (width / 4)
        self.horizon = int(self.horizon_base + offset * 0.1)

        slices = 12
        road_top = road_w * 0.2
        prev_center = width / 2
        prev_width = road_w
        prev_y = bottom
        for i in range(slices):
            t1 = (i + 1) / slices
            y = bottom - (bottom - self.horizon) * t1
            center = width / 2 + offset * t1
            w = road_w - (road_w - road_top) * t1
            points = [
                (prev_center - prev_width / 2, prev_y),
                (prev_center + prev_width / 2, prev_y),
                (center + w / 2, y),
                (center - w / 2, y),
            ]
            pygame.draw.polygon(self.screen, (60, 60, 60), points)
            prev_center, prev_width, prev_y = center, w, y

        # center line segmented along the curve
        prev_center = width / 2
        prev_y = bottom
        for i in range(slices):
            t = (i + 1) / slices
            y = bottom - (bottom - self.horizon) * t
            center = width / 2 + offset * t
            pygame.draw.line(
                self.screen,
                (255, 255, 255),
                (prev_center, prev_y),
                (center, y),
                2,
            )
            prev_center, prev_y = center, y

        # Obstacles rendered as roadside billboards
        player = env.cars[0]
        for obs in getattr(env.track, "obstacles", []):
            dx = (obs.x - player.x) % env.track.width
            scale = max(0.1, min(1.0 / (dx / 5.0 + 1.0), 1.0))
            o_h = 15 * scale
            o_w = obs.width * scale
            ox = width / 2 + (obs.y - env.track.height / 2) - offset * (1.0 - scale)
            oy = bottom - (bottom - self.horizon) * scale
            rect = pygame.Rect(int(ox - o_w / 2), int(oy - o_h), int(o_w), int(o_h))
            if self.billboard_sprite:
                img = pygame.transform.scale(self.billboard_sprite, rect.size)
                self.screen.blit(img, rect)
            else:
                pygame.draw.rect(self.screen, (200, 200, 200), rect)

        # Render the opponent car scaled by distance
        other = env.cars[1]
        dist = (other.x - player.x) % env.track.width
        scale = max(0.1, min(1.0 / (dist / 5.0 + 1.0), 1.0))
        car_h = 20 * scale
        car_w = 10 * scale
        x = width / 2 - offset * (1.0 - scale)
        y = bottom - (bottom - self.horizon) * scale
        rect = pygame.Rect(int(x - car_w / 2), int(y - car_h), int(car_w), int(car_h))
        if self.car_sprite:
            img = pygame.transform.scale(self.car_sprite, rect.size)
            self.screen.blit(img, rect)
        else:
            pygame.draw.rect(self.screen, self.car_color, rect)

        if env.crash_timer > 0:
            self.draw_explosion(env, (int(x - car_w), int(y - car_h * 2)))

        # Player HUD text
        if pygame.font:
            font = pygame.font.SysFont(None, 24)
            hi_score = max(HIGH_SCORE, int(env.score))
            hi_text = font.render(f"HI {hi_score:06d}", True, (0, 255, 0))
            score_text = font.render(f"SCORE {int(env.score):06d}", True, (0, 255, 0))
            self.screen.blit(hi_text, (10, 10))
            self.screen.blit(score_text, (10, 30))

            # center timer & lap timer
            time_text = font.render(f"TIME {env.remaining_time:05.2f}", True, (255, 255, 0))
            tx = width // 2 - time_text.get_width() // 2
            self.screen.blit(time_text, (tx, 10))
            lap_val = env.lap_timer if env.lap_flash <= 0 else env.last_lap_time
            if lap_val is not None:
                lap_time_text = font.render(f"LAP {lap_val:05.2f}", True, (0, 255, 0))
                lx = width // 2 - lap_time_text.get_width() // 2
                self.screen.blit(lap_time_text, (lx, 30))

            lap_text = font.render(f"LAP {env.lap + 1}/4", True, (0, 255, 0))
            p_prog = env.track.progress(player)
            o_prog = env.track.progress(other)
            pos = 1 if p_prog >= o_prog else 2
            pos_text = font.render(f"POS {pos}/2", True, (0, 255, 0))
            self.screen.blit(lap_text, (10, 50))
            self.screen.blit(pos_text, (10, 70))

            mph = int(player.speed * 2.23694)
            spd_text = font.render(f"SPEED {mph} MPH", True, (255, 255, 255))
            gear = "H" if player.gear else "L"
            gear_text = font.render(f"GEAR {gear}", True, (255, 255, 255))
            self.screen.blit(spd_text, (width - spd_text.get_width() - 10, 10))
            self.screen.blit(gear_text, (width - gear_text.get_width() - 10, 30))

            perf_lines = []
            if os.environ.get("PERF_HUD", "0") != "0":
                if getattr(env, "step_durations", []):
                    perf_lines.append(
                        f"step {env.step_durations[-1]*1000:.1f} ms"
                    )
                if getattr(env, "plan_durations", []):
                    perf_lines.append(
                        f"plan {env.plan_durations[-1]*1000:.1f} ms"
                    )
                if getattr(env, "plan_tokens", []):
                    perf_lines.append(
                        f"tok {env.plan_tokens[-1]}"
                    )
            for i, line in enumerate(perf_lines):
                t = font.render(line, True, (255, 255, 255))
                self.screen.blit(t, (width - 160, 30 + 20 * i))

            # mini-map simple dot positions
            map_h = 80
            map_w = 80
            pygame.draw.rect(
                self.screen,
                (30, 30, 30),
                pygame.Rect(width - map_w - 10, 10, map_w, map_h),
                1,
            )
            px = width - map_w - 10 + (player.x / env.track.width) * map_w
            py = 10 + (player.y / env.track.height) * map_h
            ox = width - map_w - 10 + (other.x / env.track.width) * map_w
            oy = 10 + (other.y / env.track.height) * map_h
            pygame.draw.circle(self.screen, (255, 0, 0), (int(px), int(py)), 3)
            pygame.draw.circle(self.screen, (0, 255, 0), (int(ox), int(oy)), 3)

        # Scanline effect

        if self.scanline_alpha > 0:
            row = pygame.Surface((width, 1))
            row.fill((0, 0, 0))
            row.set_alpha(self.scanline_alpha)
            for y in range(0, height, self.scanline_spacing):
                self.screen.blit(row, (0, y))

        if self._scanline_row:
            row = pygame.transform.scale(self._scanline_row, (width, 1))
            for y in range(0, height, self.scanline_step):
                self.screen.blit(row, (0, y))
