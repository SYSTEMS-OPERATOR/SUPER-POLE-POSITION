"""Simple CPU opponent logic."""

from dataclasses import dataclass, field
from random import Random

from .physics.car import Car
from .physics.track import Track


@dataclass
class CPUCar(Car):
    """Rudimentary AI-controlled car with simple lane changes."""

    x: float = 0.0
    y: float = 0.0
    angle: float = 0.0
    speed: float = 0.0
    preferred_lane: float = 0.0
    target_speed: float = 5.0
    state: str = "CRUISE"
    _block_time: float = field(default=0.0, init=False)
    _block_cooldown: float = field(default=0.0, init=False)
    _lane_timer: float = field(default=0.0, init=False)
    rng: Random = field(default_factory=Random, repr=False)

    def __post_init__(self) -> None:
        super().__init__(self.x, self.y, self.angle, self.speed)
        self.preferred_lane = self.y
        self._lane_timer = self.rng.uniform(2.0, 4.0)

    def blocking(self, player: Car, track: Track) -> bool:
        """Return ``True`` if player is close enough behind to block."""

        behind = (self.x - player.x) % track.width
        same_lane = abs(self.y - player.y) < 0.5
        return 0 < behind <= 7.0 and same_lane


    def update(self, dt: float, track: Track, player: Car) -> None:
        """Advance AI state machine."""

        self._block_cooldown = max(self._block_cooldown - dt, 0.0)

        if (
            self.state == "CRUISE"
            and self._block_cooldown <= 0.0
            and self.blocking(player, track)
        ):
            self.state = "BLOCK"
            self._block_time = 1.0
            self._block_cooldown = 2.0

        if self.state == "CRUISE":
            self._lane_timer -= dt
            if self._lane_timer <= 0.0:
                offset = self.rng.choice([-1.0, 0.0, 1.0])
                self.preferred_lane = track.y_at(self.x) + offset
                self._lane_timer = self.rng.uniform(2.0, 4.0)
            diff = self.preferred_lane - self.y
            self.y += diff * dt * 0.5

        if self.state == "BLOCK":
            direction = -1.0 if player.y > self.y else 1.0
            self.y += direction * dt
            self._block_time -= dt
            if self._block_time <= 0:
                self.state = "RECOVER"

        if self.state == "RECOVER":
            diff = self.preferred_lane - self.y
            if abs(diff) < 0.1:
                self.state = "CRUISE"
            else:
                self.y += diff * dt

        self.y = max(0.0, min(track.height, self.y))

    def policy(self, track: Track | None = None):
        """Return throttle, brake, steer for basic cruising."""

        throttle = self.speed < self.target_speed
        brake = self.speed > self.target_speed
        steer = 0.0
        if track is not None:
            target_y = track.y_at(self.x)
            offset = target_y - self.y
            steer = max(-1.0, min(1.0, offset * 0.05))
        return throttle, brake, steer
