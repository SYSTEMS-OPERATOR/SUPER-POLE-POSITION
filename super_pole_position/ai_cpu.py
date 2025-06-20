"""Simple CPU opponent logic."""

from dataclasses import dataclass, field

from .physics.car import Car
from .physics.track import Track


@dataclass
class CPUCar(Car):
    """Rudimentary AI-controlled car."""

    x: float = 0.0
    y: float = 0.0
    angle: float = 0.0
    speed: float = 0.0
    preferred_lane: float = 0.0
    state: str = "CRUISE"
    _block_time: float = field(default=0.0, init=False)

    def __post_init__(self) -> None:
        super().__init__(self.x, self.y, self.angle, self.speed)

    def blocking(self, player: Car) -> bool:
        """Return ``True`` if player is close enough to trigger blocking."""

        behind = self.x - player.x
        if behind < 0:
            behind +=  self.max_speed * 2  # track wrap approx
        same_lane = abs(self.y - player.y) < 0.5
        return behind <= 7.0 and same_lane

    def update(self, dt: float, track: Track, player: Car) -> None:
        """Advance AI state machine."""

        if self.state == "CRUISE" and self.blocking(player):
            self.state = "BLOCK"
            self._block_time = 1.0

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
