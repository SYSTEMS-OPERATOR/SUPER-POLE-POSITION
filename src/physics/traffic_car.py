from __future__ import annotations

import random
from .car import Car
from .constants import KMH_TO_MS
from .track import Track


class TrafficCar(Car):
    """Non-player car that stays on the track and avoids the player."""

    def __init__(self, track: Track, player_ref: Car, rng: random.Random = random) -> None:
        super().__init__()
        self.track = track
        self.player = player_ref
        self.rng = rng
        self.x: float = rng.uniform(0, track.lap_length)
        self.lane: int = rng.choice([-1, 1])
        self.y: float = self.lane * 2.5
        self.speed_kmh = player_ref.speed_kmh + rng.uniform(-40, 20)
        self._switch_timer: float = 0.0

    # ------------------------------------------------------------------
    def update(self, dt: float = 1 / 60) -> None:
        """Advance AI and position."""

        # Maintain constant speed using base car logic
        super().update(0.0, 0.0, dt)
        self.x = (self.x + self.speed_kmh * KMH_TO_MS * dt) % self.track.lap_length

        player = self.player
        track = self.track

        # Lane-switch detection
        d = (self.x - getattr(player, "x", 0.0) + track.lap_length) % track.lap_length
        if 0 < d < 40 and abs(self.y - getattr(player, "y", 0.0)) < 1.0:
            if self._switch_timer == 0:
                self._switch_timer = 0.3

        if self._switch_timer > 0:
            self._switch_timer -= dt
            if self._switch_timer <= 0:
                self.lane *= -1
                self.y = self.lane * 2.5

        # Respawn far behind player
        behind = (getattr(player, "x", 0.0) - self.x + track.lap_length) % track.lap_length
        if behind > 200:
            self.x = (getattr(player, "x", 0.0) + 300) % track.lap_length
            self.lane = self.rng.choice([-1, 1])
            self.y = self.lane * 2.5
            self.speed_kmh = getattr(player, "speed_kmh", 0.0) + self.rng.uniform(-40, 20)
            self._switch_timer = 0.0
