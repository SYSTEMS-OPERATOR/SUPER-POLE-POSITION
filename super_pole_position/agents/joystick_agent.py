#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Joystick controls with analog steering and throttle. 🕹️"""

from __future__ import annotations

import os
from dataclasses import dataclass

# Hide pygame's greeting for cleaner logs
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

try:
    import pygame  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    pygame = None

from .base_llm_agent import BaseLLMAgent


@dataclass
class JoystickConfig:
    """Configuration for axis/button mapping."""

    steer_axis: int = 0
    throttle_axis: int = 1
    brake_axis: int | None = None
    shift_up_button: int | None = None
    shift_down_button: int | None = None
    dead_zone: float = 0.05


class JoystickAgent(BaseLLMAgent):
    """Human agent using a physical joystick or wheel."""

    def __init__(self, config: JoystickConfig | None = None) -> None:
        self.config = config or JoystickConfig()
        self.joystick = None
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

        steer = self._axis(self.config.steer_axis)
        throttle_val = -self._axis(self.config.throttle_axis)
        throttle = max(0.0, min(1.0, (throttle_val + 1) / 2))

        brake = 0.0
        if self.config.brake_axis is not None:
            brake_val = self._axis(self.config.brake_axis)
            brake = max(0.0, min(1.0, (brake_val + 1) / 2))

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
