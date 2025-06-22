"""Simple SFX wrapper around ``pygame.mixer``."""

from __future__ import annotations

import pathlib
import pygame

# Map sound effect names to mixer channels
CHANNEL_MAP = {
    "engine": 0,
    "skid": 1,
    "crash": 2,
    "checkpoint": 3,
}


class Sfx:
    """Lightweight sound effect object with lazy loading."""

    _cache: dict[str, pygame.mixer.Sound] = {}

    def __init__(self, name: str, path: pathlib.Path, loop: bool = False) -> None:
        self.name = name
        self.loop = loop
        self.path = path
        self.sound: pygame.mixer.Sound | None = None

    def _ensure(self) -> None:
        """Load the sound if it hasn't been loaded yet."""

        if self.sound is None:
            self.sound = pygame.mixer.Sound(self.path)
            Sfx._cache[self.name] = self.sound

    # ------------------------------------------------------------------
    def play(self, volume: float = 1.0) -> bool:
        """Play the sound on its dedicated channel."""

        self._ensure()
        ch = pygame.mixer.Channel(CHANNEL_MAP[self.name])
        ch.set_volume(volume)
        ch.play(self.sound, loops=-1 if self.loop else 0)
        return True

    def stop(self) -> bool:
        """Stop playback on the assigned channel."""

        ch = pygame.mixer.Channel(CHANNEL_MAP[self.name])
        ch.stop()
        return True

    def set_pitch(self, semitones: float) -> None:
        """Adjust pitch if supported by the SDL2 backend."""

        if self.sound:
            try:
                self.sound.set_pitch(2 ** (semitones / 12))
            except AttributeError:
                pass

