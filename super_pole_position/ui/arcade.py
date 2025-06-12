"""Minimal pygame viewer used during local races.

HUD elements use a simple CRT-style effect with a dark green palette. The
scanline spacing and brightness are tuned via the ``Palette`` class in this
module.
"""

import os
from pathlib import Path

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
        self.explosion = None
        if pygame:
            exp_path = (
                Path(__file__).resolve().parent.parent / "assets" / "explosion_16f.png"
            )
            try:
                # Sprite sheet not bundled; will be added later.
                self.explosion = pygame.image.load(str(exp_path))
            except Exception:
                self.explosion = None

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
        if self.font:
            speed = int(env.cars[0].speed * 3.6)
            gear = "H" if env.cars[0].gear else "L"
            text = self.font.render(f"{speed} km/h G:{gear}", True, (255, 255, 255))
            self.screen.blit(text, (10, 10))

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
        self.horizon = int(screen.get_height() * 0.4)
        self.sky_color = (100, 150, 255)
        self.ground_color = (40, 40, 40)
        self.car_color = (255, 0, 0)
        self.car_sprite = ascii_surface(CAR_ART)
        self.billboard_sprite = ascii_surface(BILLBOARD_ART)
        self.explosion_frames = [ascii_surface(f) for f in EXPLOSION_FRAMES]

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

        # road trapezoid (vanishing point shifts with car angle)
        road_w = width * 0.6
        bottom = height
        player = env.cars[0]
        # ``curve`` is roughly -1.0..1.0 based on steering angle
        curve = max(-1.0, min(player.angle / 0.5, 1.0))
        offset = curve * width * 0.15

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

        if env.crash_timer > 0 and self.explosion_frames:
            phase = (2.5 - env.crash_timer) / 2.5
            idx = min(
                int(phase * (len(self.explosion_frames) - 1)),
                len(self.explosion_frames) - 1,
            )
            exp = pygame.transform.scale(
                self.explosion_frames[idx], (int(car_w * 2), int(car_h * 2))
            )
            self.screen.blit(exp, (int(x - car_w), int(y - car_h * 2)))
        elif env.crash_timer > 0 and self.explosion:
            exp = pygame.transform.scale(
                self.explosion, (int(car_w * 2), int(car_h * 2))
            )
            self.screen.blit(exp, (int(x - car_w), int(y - car_h * 2)))

        # Player HUD text
        if pygame.font:
            font = pygame.font.SysFont(None, 24)
            hi_score = max(HIGH_SCORE, int(env.score))
            hi_text = font.render(f"HI {hi_score:06d}", True, (0, 255, 0))
            score_text = font.render(f"SCORE {int(env.score):06d}", True, (0, 255, 0))
            self.screen.blit(hi_text, (10, 10))
            self.screen.blit(score_text, (10, 30))

            lap_text = font.render(f"LAP {env.lap + 1}/4", True, (0, 255, 0))
            time_text = font.render(
                f"TIME {env.remaining_time:05.2f}", True, (0, 255, 0)
            )
            pos = 1 if env.track.distance(player, other) < 0 else 2
            pos_text = font.render(f"POS {pos}/2", True, (0, 255, 0))
            self.screen.blit(lap_text, (10, 50))
            self.screen.blit(time_text, (10, 70))
            self.screen.blit(pos_text, (10, 90))

            spd = int(player.speed * 3.6)
            spd_text = font.render(f"{spd} km/h", True, (255, 255, 255))
            self.screen.blit(spd_text, (10, 110))

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
        for y in range(0, height, 2):
            pygame.draw.line(self.screen, (0, 0, 0), (0, y), (width, y), 1)
