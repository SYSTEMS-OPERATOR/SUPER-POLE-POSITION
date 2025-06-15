from dataclasses import dataclass


@dataclass
class CarState:
    """Simple dataclass for serialising car state."""

    x: float
    y: float
    speed: float
    angle: float
    lap: int = 0
    damage: float = 0.0
