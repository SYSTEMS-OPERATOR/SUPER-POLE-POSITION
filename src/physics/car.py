from __future__ import annotations

from dataclasses import dataclass, field

from .constants import GRAVITY, KMH_TO_MS


MAX_SPEED_HIGH: float = 318.0  # km/h
MAX_SPEED_LOW: float = 113.0

# Coefficients tuned for arcade feel
ACCEL_COEFF_LOW: float = 0.5381814239482186
ACCEL_COEFF_HIGH: float = 3.698426992090258

# Steering gain so 200 mph gives ~0.8 g when steer=1
STEER_GAIN: float = (0.8 * GRAVITY) / ((200 * 1.60934 / 3.6) ** 2)

SKID_DURATION: float = 0.5


@dataclass
class Car:
    speed_kmh: float = 0.0
    gear: str = "LOW"
    skid_timer: float = 0.0
    heading: float = 0.0
    a_lat: float = 0.0
    _over_g: bool = field(default=False, init=False, repr=False)

    # ------------------------------------------------------------------
    def update(self, throttle: float, steer_in: float, dt: float = 1 / 60) -> None:
        """Advance the car simulation by ``dt`` seconds."""
        if self.skid_timer > 0.0:
            self.speed_kmh *= 0.92
            self.skid_timer = max(self.skid_timer - dt, 0.0)
            self.a_lat = 0.0
            return

        if self.gear == "LOW" and throttle >= 0.8 and self.speed_kmh >= 105.0:
            self.shift_high()

        target = MAX_SPEED_HIGH if self.gear == "HIGH" else MAX_SPEED_LOW
        coeff = ACCEL_COEFF_HIGH if self.gear == "HIGH" else ACCEL_COEFF_LOW
        self.speed_kmh += (target - self.speed_kmh) * coeff * throttle * dt
        if self.speed_kmh > target:
            self.speed_kmh = target

        curvature = STEER_GAIN * steer_in
        self.heading += (self.speed_kmh * KMH_TO_MS) * curvature * dt
        self.a_lat = (self.speed_kmh * KMH_TO_MS) ** 2 * abs(curvature)

        if self.a_lat > GRAVITY:
            if self._over_g:
                self.skid_timer = SKID_DURATION
            self._over_g = True
        else:
            self._over_g = False

    # ------------------------------------------------------------------
    def shift_high(self) -> None:
        self.gear = "HIGH"

    # ------------------------------------------------------------------
    def shift_low(self) -> None:
        self.gear = "LOW"


"""
── Original Panda3D snippet (grid_leader/vehicle.py) ───────────────────
MAX_SPEED_HIGH = 318.0  # km/h
MAX_SPEED_LOW  = 113.0
ACCEL_COEFF    = 0.45   # tuned so 0‑>MAX ≈4s

def update(dt):
    if throttle:
        v += (max_speed - v) * ACCEL_COEFF * dt
    else:
        v -= drag * dt
    if gear == LOW and v > MAX_SPEED_LOW - 2:
        auto_shift_high()
    # steer
    curvature = STEER_GAIN * steer_input
    a_lat = (v_kmh*KMH2MS)**2 * curvature
    if a_lat > 9.81:
        skid_timer = 0.5
"""
