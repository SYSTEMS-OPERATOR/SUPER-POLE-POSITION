"""Minimal pygame viewer used during local races."""
import os

try:
    import pygame  # type: ignore
except Exception:  # pragma: no cover
    pygame = None


def available() -> bool:
    return pygame is not None


class ArcadeRenderer:
    """Draw HUD and scenery layers using pygame."""

    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont(None, 24) if pygame else None
        self.scenery = []
        if pygame:
            import pathlib
            sc_dir = pathlib.Path(__file__).resolve().parent.parent / "assets" / "scenery"
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
            self.crash_sound = silent

    def draw(self, env) -> None:
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
            pitch = env.cars[0].speed / env.cars[0].gear_max[-1]
            self.channels[0].play(self.engine_sound, loops=-1)
            if abs(env.cars[0].angle) > 0.7 and env.cars[0].speed > 50:
                self.channels[1].play(self.skid_sound)
            if env.crash_timer > 0 and not self.channels[2].get_busy():
                self.channels[2].play(self.crash_sound)
