#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 MIND INTERFACES, INC. All rights reserved.
# Licensed under the MIT License.

"""
arcade.py
Description: Module for Super Pole Position.
"""


import os
import math

# Hide pygame's greeting for cleaner logs
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
from pathlib import Path
from typing import Dict


from ..config import load_parity_config
from .sprites import (
    BILLBOARD_ART,
    CAR_ART,
    EXPLOSION_FRAMES,
    ascii_surface,
)
from ..evaluation.scores import load_scores


_AUDIO_CFG = load_parity_config()
AUDIO_VOLUME = float(_AUDIO_CFG.get("audio_volume", 0.8))


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

try:
    HIGH_SCORE = max((s["score"] for s in load_scores(None)), default=0)
except Exception:  # pragma: no cover - file may be missing
    HIGH_SCORE = 0

try:
    import pygame  # type: ignore
except Exception:  # pragma: no cover
    pygame = None


def _load_sprite(name: str) -> "pygame.Surface | None":
    """Return image surface from ``assets/sprites`` or ``None`` if missing."""

    if not pygame:
        return None
    path = Path(__file__).resolve().parents[2] / "assets" / "sprites" / name
    try:
        surf = pygame.image.load(str(path))
        return surf.convert_alpha()
    except Exception:
        return None


def _load_arcade_config() -> Dict[str, float]:
    """Return scanline configuration from ``config.arcade_parity.yaml``."""

    cfg: Dict[str, float] = {"scanline_step": 2, "scanline_alpha": 255, "horizon_sway": 0.1}
    path = Path(__file__).resolve().parents[2] / "config.arcade_parity.yaml"
    try:
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                if ":" not in line:
                    continue
                key, val = line.split(":", 1)
                try:
                    val = val.strip()
                    cfg[key.strip()] = float(val) if "." in val else int(val)
                except Exception:
                    # Ignore non-numeric values and keep defaults
                    continue
    except Exception:
        pass
    return cfg


HORIZON_SWAY = float(_load_arcade_config().get("horizon_sway", 0.1))


class Palette:
    """Arcade cabinet palette with basic NTSC gamma approximation."""

    black = (0, 0, 0)
    white = (255, 255, 255)
    red = (255, 48, 48)
    green = (0, 184, 0)
    blue = (80, 112, 255)
    yellow = (255, 216, 0)
    grey = (60, 60, 60)
    sky_blue = (116, 204, 221)


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
            for ch in self.channels:
                ch.set_volume(AUDIO_VOLUME)
            silent = pygame.mixer.Sound(buffer=b"\0\0")
            silent.set_volume(AUDIO_VOLUME)
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
                self.crash_sound.set_volume(AUDIO_VOLUME)
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
        score_text = (
            f"SCORE {int(env.score):05d}  HI {int(getattr(env, 'high_score', 0)):05d}"
        )
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
        time_text = self.font.render(
            f"TIME {env.remaining_time:05.2f}", True, (255, 255, 0)
        )
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
    Objects are drawn with a simple 1/z perspective relative to the player's
    car along the x-axis.  The road converges toward a vanishing point on the
    horizon using linear interpolation.  The horizon shifts based on the
    player's steering angle to mimic curves. ``horizon_sway`` controls this
    shift for finer arcade parity tuning.
    """

    def __init__(self, screen):
        """Create the renderer bound to ``screen`` with an optional high-res buffer.

        ``horizon_sway`` is loaded from :mod:`config.arcade_parity.yaml` and
        controls how dramatically the vanishing point shifts on curves.
        """

        self.screen = screen
        if pygame and not pygame.font.get_init():
            pygame.font.init()
        self.render_scale = 2
        if pygame:
            self.offscreen = pygame.Surface(
                (
                    screen.get_width() * self.render_scale,
                    screen.get_height() * self.render_scale,
                )
            )
        else:
            self.offscreen = None
        self.horizon_base = int(screen.get_height() * 0.4)
        self.horizon = self.horizon_base
        # Sky gradient colors roughly matching the arcade palette
        self.sky_top = Palette.sky_blue
        self.sky_bottom = (80, 160, 208)
        self.sky_color = Palette.sky_blue
        self.ground_color = Palette.grey
        self.car_color = Palette.red
        self.player_car_sprite = _load_sprite("player_car.png") or ascii_surface(
            CAR_ART
        )
        self.cpu_front_sprite = _load_sprite("cpu_car.png") or ascii_surface(CAR_ART)
        self.billboard_sprites = []
        for i in range(1, 9):
            spr = _load_sprite(f"billboard_{i}.png")
            if spr:
                self.billboard_sprites.append(spr)
        if not self.billboard_sprites:
            self.billboard_sprites = [ascii_surface(BILLBOARD_ART)]
        self.mt_fuji = _load_sprite("mt_fuji.png")
        self.clouds = _load_sprite("clouds.png")
        self.cloud_offset = 0.0
        sheet = _load_sprite("explosion_16f.png")
        if sheet:
            frame_w = sheet.get_width() // 16
            self.explosion_frames = [
                sheet.subsurface((i * frame_w, 0, frame_w, sheet.get_height()))
                for i in range(16)
            ]
        else:
            self.explosion_frames = [ascii_surface(f) for f in EXPLOSION_FRAMES]
        self.scanline_spacing = SCANLINE_SPACING
        self.scanline_alpha = SCANLINE_ALPHA

        cfg = _load_arcade_config()
        self.scanline_step = cfg["scanline_step"]
        self.scanline_alpha = cfg["scanline_alpha"]
        self.horizon_sway = float(cfg.get("horizon_sway", HORIZON_SWAY))
        if pygame:
            self._scanline_row = pygame.Surface((1, 1), pygame.SRCALPHA)
            self._scanline_row.fill((0, 0, 0, self.scanline_alpha))
            self.start_font = pygame.font.SysFont(None, 48)
            self.canvas = self.offscreen
        else:
            self._scanline_row = None
            self.start_font = None
            self.canvas = screen
        self.dash_offset = 0.0

    def road_polygon(self, offset: float) -> list[tuple[float, float]]:
        """Return trapezoid points for the road given ``offset``."""

        surface = self.canvas
        scale = self.render_scale if self.offscreen else 1
        width = surface.get_width()
        height = surface.get_height()
        road_w = width * 0.6
        road_top = road_w * 0.2
        points = [
            (width / 2 - road_w / 2, height),
            (width / 2 + road_w / 2, height),
            (width / 2 + offset + road_top / 2, self.horizon),
            (width / 2 + offset - road_top / 2, self.horizon),
        ]
        return [(x / scale, y / scale) for x, y in points]

    def draw_road_polygon(self, env) -> list[tuple[float, float]]:
        """Draw the road trapezoid and return its points."""

        angle = env.track.angle_at(env.cars[0].x)
        curvature = max(-1.0, min(angle / (math.pi / 4), 1.0))
        offset = curvature * (self.canvas.get_width() / 4)
        points = self.road_polygon(offset)
        if pygame:
            scaled = [
                (
                    x * (self.render_scale if self.offscreen else 1),
                    y * (self.render_scale if self.offscreen else 1),
                )
                for x, y in points
            ]
            pygame.draw.polygon(self.canvas, (60, 60, 60), scaled)
        return points

    def _draw_sky(self, surface: "pygame.Surface") -> None:
        """Render a vertical sky gradient above the horizon."""

        for y in range(self.horizon):
            t = y / max(1, self.horizon - 1)
            r = int(self.sky_top[0] * (1 - t) + self.sky_bottom[0] * t)
            g = int(self.sky_top[1] * (1 - t) + self.sky_bottom[1] * t)
            b = int(self.sky_top[2] * (1 - t) + self.sky_bottom[2] * t)
            pygame.draw.line(surface, (r, g, b), (0, y), (surface.get_width(), y))

    def draw(self, env) -> None:
        """Draw the environment from a front-facing perspective."""

        if not pygame:
            return

        surface = self.canvas
        width = surface.get_width()
        height = surface.get_height()

        # sky gradient and ground fill
        self._draw_sky(surface)
        pygame.draw.rect(
            surface,
            self.ground_color,
            (0, self.horizon, width, height - self.horizon),
        )
        if self.mt_fuji:
            mx = width // 2 - self.mt_fuji.get_width() // 2
            my = self.horizon - self.mt_fuji.get_height()
            surface.blit(self.mt_fuji, (mx, my))
        if self.clouds:
            self.cloud_offset = (
                self.cloud_offset + env.cars[0].x * 0.02
            ) % self.clouds.get_width()
            for off in (
                -self.cloud_offset,
                -self.cloud_offset + self.clouds.get_width(),
            ):
                surface.blit(
                    self.clouds,
                    (int(off), self.horizon - self.clouds.get_height() - 10),
                )

        # road trapezoid (vanishing point shifts with curvature)
        road_w = width * 0.6
        bottom = height
        player = env.cars[0]
        angle = env.track.angle_at(player.x)
        curvature = max(-1.0, min(angle / (math.pi / 4), 1.0))
        offset = curvature * (width / 4)
        self.horizon = int(self.horizon_base + offset * self.horizon_sway)

        slices = 64
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
            shade = int(60 + 70 * t1)
            road_color = (shade, shade, shade)
            pygame.draw.polygon(surface, road_color, points)
            stripe_base = (255, 0, 0) if i % 2 == 0 else (255, 255, 255)
            shade_factor = 1.0 - t1 * 0.3
            stripe_color = tuple(int(c * shade_factor) for c in stripe_base)
            pygame.draw.line(
                surface,
                stripe_color,
                (points[0][0], points[0][1]),
                (points[3][0], points[3][1]),
                2,
            )
            pygame.draw.line(
                surface,
                stripe_color,
                (points[1][0], points[1][1]),
                (points[2][0], points[2][1]),
                2,
            )
            prev_center, prev_width, prev_y = center, w, y

        # center dashed line following car speed
        prev_center = width / 2
        prev_y = bottom
        self.dash_offset = (self.dash_offset + player.speed * 0.1) % 2
        for i in range(slices):
            t = (i + 1) / slices
            y = bottom - (bottom - self.horizon) * t
            center = width / 2 + offset * t
            if int(i + self.dash_offset) % 2 == 0:
                pygame.draw.line(
                    surface,
                    (255, 255, 255),
                    (prev_center, prev_y),
                    (center, y),
                    2,
                )
            prev_center, prev_y = center, y

        # draw finish line when near the start point
        progress_to_start = (player.x - env.track.start_x) % env.track.width
        if progress_to_start < player.speed * 1.5 + 2:
            step = road_w / 10
            y0 = bottom - 12
            for i in range(10):
                color = (255, 255, 255) if i % 2 else (0, 0, 0)
                x0 = width / 2 - road_w / 2 + i * step
                rect = pygame.Rect(int(x0), int(y0), int(step), 12)
                pygame.draw.rect(surface, color, rect)

        # Obstacles rendered as roadside billboards
        player = env.cars[0]
        for idx, obs in enumerate(getattr(env.track, "obstacles", [])):
            dx = (obs.x - player.x) % env.track.width
            scale = max(0.1, min(1.0 / (dx / 5.0 + 1.0), 1.0))
            o_h = 15 * scale
            o_w = obs.width * scale
            ox = width / 2 + (obs.y - env.track.height / 2) - offset * (1.0 - scale)
            oy = bottom - (bottom - self.horizon) * scale
            rect = pygame.Rect(int(ox - o_w / 2), int(oy - o_h), int(o_w), int(o_h))
            sprite = self.billboard_sprites[idx % len(self.billboard_sprites)]
            if sprite:
                img = pygame.transform.scale(sprite, rect.size)
                surface.blit(img, rect)
            else:
                pygame.draw.rect(surface, (200, 200, 200), rect)

        # Render the opponent car scaled by distance
        other = env.cars[1]
        dist = (other.x - player.x) % env.track.width
        scale = max(0.1, min(1.0 / (dist / 5.0 + 1.0), 1.0))
        car_h = 20 * scale
        car_w = 10 * scale
        x = width / 2 - offset * (1.0 - scale)
        y = bottom - (bottom - self.horizon) * scale
        rect = pygame.Rect(int(x - car_w / 2), int(y - car_h), int(car_w), int(car_h))
        sprite = self.player_car_sprite
        if dist < env.track.width / 2:
            sprite = self.cpu_front_sprite
        if sprite:
            img = pygame.transform.scale(sprite, rect.size)
            surface.blit(img, rect)
        else:
            pygame.draw.rect(surface, self.car_color, rect)

        if env.crash_timer > 0:
            self.draw_explosion(env, (int(x - car_w), int(y - car_h * 2)))

        # Player HUD text
        if pygame.font:
            font = pygame.font.SysFont(None, 24)
            hi_score = max(HIGH_SCORE, int(env.score))
            hi_text = font.render(f"HI {hi_score:06d}", True, (0, 255, 0))
            score_text = font.render(f"SCORE {int(env.score):06d}", True, (0, 255, 0))
            surface.blit(hi_text, (10, 10))
            surface.blit(score_text, (10, 30))

            # center timer & lap timer
            time_text = font.render(
                f"TIME {env.remaining_time:05.2f}", True, (255, 255, 0)
            )
            tx = width // 2 - time_text.get_width() // 2
            surface.blit(time_text, (tx, 10))
            lap_val = env.lap_timer if env.lap_flash <= 0 else env.last_lap_time
            if lap_val is not None:
                lap_time_text = font.render(f"LAP {lap_val:05.2f}", True, (0, 255, 0))
                lx = width // 2 - lap_time_text.get_width() // 2
                surface.blit(lap_time_text, (lx, 30))

            lap_text = font.render(f"LAP {env.lap + 1}/4", True, (0, 255, 0))
            p_prog = env.track.progress(player)
            o_prog = env.track.progress(other)
            pos = 1 if p_prog >= o_prog else 2
            pos_text = font.render(f"POS {pos}/2", True, (0, 255, 0))
            surface.blit(lap_text, (10, 50))
            surface.blit(pos_text, (10, 70))

            mph = int(player.speed * 2.23694)
            spd_text = font.render(f"SPEED {mph} MPH", True, (255, 255, 255))
            gear = "H" if player.gear else "L"
            gear_text = font.render(f"GEAR {gear}", True, (255, 255, 255))
            surface.blit(spd_text, (width - spd_text.get_width() - 10, 10))
            surface.blit(gear_text, (width - gear_text.get_width() - 10, 30))

            perf_lines = []
            if os.environ.get("PERF_HUD", "0") != "0":
                if getattr(env, "step_durations", []):
                    perf_lines.append(f"step {env.step_durations[-1]*1000:.1f} ms")
                if getattr(env, "plan_durations", []):
                    perf_lines.append(f"plan {env.plan_durations[-1]*1000:.1f} ms")
                if getattr(env, "plan_tokens", []):
                    perf_lines.append(f"tok {env.plan_tokens[-1]}")
        for i, line in enumerate(perf_lines):
            t = font.render(line, True, (255, 255, 255))
            surface.blit(t, (width - 160, 30 + 20 * i))

            # mini-map simple dot positions
            map_h = 80
            map_w = 80
            pygame.draw.rect(
                surface,
                (30, 30, 30),
                pygame.Rect(width - map_w - 10, 10, map_w, map_h),
                1,
            )
            px = width - map_w - 10 + (player.x / env.track.width) * map_w
            py = 10 + (player.y / env.track.height) * map_h
            ox = width - map_w - 10 + (other.x / env.track.width) * map_w
            oy = 10 + (other.y / env.track.height) * map_h
            pygame.draw.circle(surface, (255, 0, 0), (int(px), int(py)), 3)
            pygame.draw.circle(surface, (0, 255, 0), (int(ox), int(oy)), 3)

        # Starting lights / ready-set-go text
        if self.start_font and env.current_step < 30:
            phase = env.start_phase
            if phase:
                color = (255, 255, 0) if phase != "GO" else (0, 255, 0)
                text = self.start_font.render(phase, True, color)
                tx = width // 2 - text.get_width() // 2
                ty = height // 2 - text.get_height() // 2
                surface.blit(text, (tx, ty))
        if self.start_font and env.message_timer > 0 and env.game_message:
            msg = self.start_font.render(env.game_message, True, (255, 255, 0))
            mx = width // 2 - msg.get_width() // 2
            my = height // 2 - msg.get_height() // 2
            surface.blit(msg, (mx, my))
            if env.game_message in {"FINISHED!", "TIME UP!"}:
                try:
                    table = load_scores(None)
                except Exception:
                    table = []
                for i, entry in enumerate(table[:5]):
                    line = f"{i+1}. {entry['name']} {entry['score']:05d}"
                    txt = self.start_font.render(line, True, (255, 255, 255))
                    tx = width // 2 - txt.get_width() // 2
                    ty = my + 40 + i * 20
                    surface.blit(txt, (tx, ty))

        if self.start_font and getattr(env, "time_extend_flash", 0) > 0:
            text = self.start_font.render("EXTENDED TIME", True, (255, 255, 0))
            tx = width // 2 - text.get_width() // 2
            ty = height // 2 + 40
            surface.blit(text, (tx, ty))

        # Scale to display and apply scanlines
        target = self.screen
        if self.offscreen:
            scaled = pygame.transform.smoothscale(self.offscreen, target.get_size())
            target.blit(scaled, (0, 0))
        else:
            target = surface

        if self._scanline_row:
            row = pygame.transform.scale(self._scanline_row, (target.get_width(), 1))
            for y in range(0, target.get_height(), self.scanline_step):
                target.blit(row, (0, y))
