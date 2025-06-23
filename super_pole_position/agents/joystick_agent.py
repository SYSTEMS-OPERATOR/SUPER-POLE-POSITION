#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Joystick controls with analog steering and throttle. 🕹️"""

from __future__ import annotations

import os
import math
from dataclasses import dataclass

# Hide pygame's greeting for cleaner logs
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

try:
    import pygame  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    pygame = None

from .base_llm_agent import BaseLLMAgent
from ..config import load_parity_config


@dataclass
class JoystickConfig:
    """Configuration for axis/button mapping."""

    steer_axis: int = 0
    throttle_axis: int = 1
    brake_axis: int | None = None
    shift_up_button: int | None = None
    shift_down_button: int | None = None
    dead_zone: float = 0.05
    disable_brake: bool = load_parity_config().get("disable_brake", False)


class JoystickAgent(BaseLLMAgent):
    """Human agent using a physical joystick or wheel."""

    def __init__(self, config: JoystickConfig | None = None) -> None:
        self.config = config or JoystickConfig()
        self.joystick = None
        env_val = os.getenv("DISABLE_BRAKE")
        if env_val is not None:
            self.config.disable_brake = env_val == "1"
        if pygame is not None:
            try:  # pragma: no cover - optional dependency
                pygame.joystick.init()
                if pygame.joystick.get_count() > 0:
                    self.joystick = pygame.joystick.Joystick(0)
                    self.joystick.init()
            except Exception:
                self.joystick = None

    def _axis(self, idx: int) -> float:
        if self.joystick is None:
            return 0.0
        val = float(self.joystick.get_axis(idx))
        if abs(val) < self.config.dead_zone:
            return 0.0
        return val

    def act(self, observation) -> dict:
        """Return action based on joystick input."""
        if pygame is None or self.joystick is None:
            return {"throttle": 0, "brake": 0, "steer": 0.0, "gear": 0}

        pygame.event.pump()

        steer_raw = self._axis(self.config.steer_axis)
        steer = math.copysign(abs(steer_raw) ** 1.5, steer_raw)
        throttle_val = -self._axis(self.config.throttle_axis)
        throttle = max(0.0, min(1.0, (throttle_val + 1) / 2)) ** 1.2

        brake = 0.0
        if self.config.brake_axis is not None:
            brake_val = self._axis(self.config.brake_axis)
            brake = max(0.0, min(1.0, (brake_val + 1) / 2))
        if self.config.disable_brake:
            brake = 0.0

        gear = 0
        if self.config.shift_up_button is not None and self.joystick.get_numbuttons() > self.config.shift_up_button:
            if self.joystick.get_button(self.config.shift_up_button):
                gear = 1
        if self.config.shift_down_button is not None and self.joystick.get_numbuttons() > self.config.shift_down_button:
            if self.joystick.get_button(self.config.shift_down_button):
                gear = -1

        return {
            "throttle": throttle,
            "brake": brake,
            "steer": steer,
            "gear": gear,
        }
