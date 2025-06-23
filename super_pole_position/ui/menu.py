#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 MIND INTERFACES, INC. All rights reserved.
# Licensed under the MIT License.

"""
menu.py
Description: Module for Super Pole Position.
"""



from __future__ import annotations

import os

# Hide pygame's greeting for cleaner logs
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
import random
from pathlib import Path

try:
    import pygame  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    pygame = None

from ..evaluation import scores as score_mod
try:  # optional audio support
    from src.audio.sfx import Sfx  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    Sfx = None  # type: ignore


def show_race_outro(screen, score: int, duration: float = 5.0) -> None:
    """Display final score and top high scores.

    When pygame is unavailable this falls back to printing the scores
    to ``stdout``. ``duration`` controls how long the overlay remains
    visible in seconds.
    """

    scores = score_mod.load_scores(None)[:5]
    if pygame is None:
        print(f"FINAL SCORE {score}")
        for i, s in enumerate(scores, 1):
            print(f"{i}. {s['name']} {s['score']}")
        return

    if screen is None:
        screen = pygame.display.set_mode((256, 224))

    font = pygame.font.SysFont(None, 24)
    clock = pygame.time.Clock()
    frames = int(duration * 30)
    count = 0
    while count < frames:
        for event in pygame.event.get():
            if event.type in {pygame.KEYDOWN, pygame.QUIT}:
                count = frames
        screen.fill((0, 0, 0))
        title = font.render("RACE OVER", True, (255, 255, 0))
        screen.blit(title, (50, 20))
        total = font.render(f"SCORE {score}", True, (255, 255, 255))
        screen.blit(total, (50, 50))
        header = font.render("TOP SCORES", True, (255, 255, 0))
        screen.blit(header, (50, 80))
        y = 110
        for i, s in enumerate(scores, 1):
            line = font.render(f"{i}. {s['name']} {s['score']}", True, (255, 255, 255))
            screen.blit(line, (50, y))
            y += 30
        pygame.display.flip()
        clock.tick(30)
        count += 1


def _show_high_scores(screen, font) -> None:
    """Display the top five scores until a key is pressed."""

    scores = score_mod.load_scores(None)[:5]
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type in {pygame.KEYDOWN, pygame.QUIT}:
                running = False
        screen.fill((0, 0, 0))
        title = font.render("HIGH SCORES", True, (255, 255, 0))
        screen.blit(title, (50, 30))
        y = 70
        for i, s in enumerate(scores, 1):
            line = font.render(f"{i}. {s['name']} {s['score']}", True, (255, 255, 255))
            screen.blit(line, (50, y))
            y += 30
        press = font.render("PRESS ANY KEY", True, (255, 255, 0))
        screen.blit(press, (50, y + 20))
        pygame.display.flip()
        clock.tick(30)


class MenuState:
    """Headless-friendly menu state machine."""

    options = {
        "difficulty": ["beginner", "expert"],
        "audio": ["on", "off"],
        "track": ["fuji", "seaside", "random"],
        "volume": list(range(0, 110, 10)),
    }
    order = ["difficulty", "audio", "track", "volume"]

    def __init__(self) -> None:
        self.values = {
            "difficulty": 0,
            "audio": 0,
            "track": 0,
            "volume": 10,
        }
        self.selected = 0

    def visible(self) -> list[str]:
        """Return list of option names currently visible."""

        if self.options_for("audio")[self.values["audio"]] == "off":
            return ["difficulty", "audio", "track"]
        return self.order

    def options_for(self, name: str) -> list:
        """Return allowed values for option ``name``."""

        return self.options[name]

    def handle(self, key: str):
        """Update state in response to a keypress."""

        key = key.upper()
        if key == "UP":
            self.selected = (self.selected - 1) % len(self.visible())
        elif key == "DOWN":
            self.selected = (self.selected + 1) % len(self.visible())
        elif key in {"LEFT", "RIGHT"}:
            name = self.visible()[self.selected]
            opts = self.options_for(name)
            delta = -1 if key == "LEFT" else 1
            self.values[name] = (self.values[name] + delta) % len(opts)
        elif key in {"ENTER", "SPACE"}:
            return self.config()
        elif key in {"ESC", "Q"}:
            return None
        return "CONTINUE"

    def config(self) -> dict:
        """Return a configuration dictionary representing the current state."""

        return {
            "difficulty": self.options_for("difficulty")[self.values["difficulty"]],
            "audio": self.options_for("audio")[self.values["audio"]] == "on",
            "track": self.options_for("track")[self.values["track"]],
            "volume": self.options_for("volume")[self.values["volume"]],
        }


# --- pygame frontend -----------------------------------------------------


def _load_backdrop(rng: random.Random) -> pygame.Surface | None:
    """Return a backdrop surface or ``None`` when pygame is unavailable."""

    if not pygame:
        return None
    bg_dir = Path(__file__).resolve().parents[2] / "assets" / "title_bg"
    files = list(bg_dir.glob("*.png"))
    if files:
        img = pygame.image.load(str(rng.choice(files)))
        return img.convert()
    # generate placeholder if no images bundled
    surf = pygame.Surface((320, 240))
    surf.fill((rng.randrange(256), rng.randrange(256), rng.randrange(256)))
    return surf


def main_loop(screen, seed: int | None = None) -> dict | None:
    """Interactive title menu loop. Returns config or None if cancelled."""
    if not pygame:
        return {
            "difficulty": "beginner",
            "audio": os.environ.get("AUDIO", "1") != "0",
            "track": "fuji",
            "volume": 100,
        }

    clock = pygame.time.Clock()
    rng = random.Random(seed)
    backdrop = _load_backdrop(rng)
    state = MenuState()
    font = pygame.font.SysFont(None, 24)
    audio_dir = Path(__file__).resolve().parents[2] / "assets" / "audio"
    try:
        if pygame.mixer and not pygame.mixer.get_init():
            pygame.mixer.init()
        tick_sfx = Sfx("menu_tick", audio_dir / "menu_tick.wav")
    except Exception:  # pragma: no cover - audio failure
        tick_sfx = None
    x_offset = 0
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                name = pygame.key.name(event.key).upper()
                result = state.handle(name)
                if tick_sfx and name in {"UP", "DOWN", "LEFT", "RIGHT", "ENTER", "SPACE"}:
                    tick_sfx.play()
                if result is None or isinstance(result, dict):
                    return result
                if name == "H":
                    _show_high_scores(screen, font)
        if backdrop:
            w = backdrop.get_width()
            screen.blit(backdrop, (-x_offset % w, 0))
            if w < screen.get_width():
                screen.blit(backdrop, ((-x_offset % w) + w, 0))
            x_offset += 1
        screen.fill((0, 0, 0)) if not backdrop else None
        # draw options
        y = 50
        for i, opt in enumerate(state.visible()):
            val = state.options_for(opt)[state.values[opt]]
            prefix = "> " if i == state.selected else "  "
            text = font.render(f"{prefix}{opt}: {val}", True, (255, 255, 255))
            screen.blit(text, (50, y))
            y += 30
        press = font.render("PRESS ENTER", True, (255, 255, 0))
        screen.blit(press, (50, y + 20))
        pygame.display.flip()
        clock.tick(30)
    return None
