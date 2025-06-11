"""Simple title menu with options and hi-score display."""

from __future__ import annotations

import os
import random
from pathlib import Path

try:
    import pygame  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    pygame = None

from ..evaluation.scores import load_scores


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
    bg_dir = Path(__file__).resolve().parent.parent / "assets" / "title_bg"
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
    x_offset = 0
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                name = pygame.key.name(event.key).upper()
                result = state.handle(name)
                if result is None or isinstance(result, dict):
                    return result
                if name == "H":
                    scores = load_scores(None)
                    print("=== HI-SCORES ===")
                    for i, s in enumerate(scores, 1):
                        print(f"{i:2d}. {s['name']} {s['score']}")
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
