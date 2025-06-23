#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Keyboard controls for your retro racer. 🎹"""

from __future__ import annotations

import os

# Hide pygame's greeting for cleaner logs
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

try:
    import pygame  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    pygame = None

from .base_llm_agent import BaseLLMAgent


class KeyboardAgent(BaseLLMAgent):
    """Human-controlled agent using the keyboard 🎮."""

    def __init__(self) -> None:
        self._last_up = False
        self._last_down = False
        self.use_virtual = False
        self.disable_brake = os.getenv("DISABLE_BRAKE", "0") == "1"
        if os.getenv("VIRTUAL_JOYSTICK", "0") == "1" and pygame is not None:
            try:  # pragma: no cover - optional dependency
                import pygame_virtual_joystick as pvj  # type: ignore

                pvj.init()
                self.use_virtual = True
            except Exception:
                self.use_virtual = False

    def act(self, observation) -> dict:
        """Return a steering command based on pressed keys."""
        if pygame is None:
            # Without pygame we return a neutral action. 🤖
            return {"throttle": 0, "brake": 0, "steer": 0.0, "gear": 0}

        if self.use_virtual:
            try:  # pragma: no cover - optional dependency
                import pygame_virtual_joystick as pvj  # type: ignore

                pvj.update()
            except Exception:
                pass

        # 🎮 Capture current key states
        keys = pygame.key.get_pressed()
        # Basic throttle/brake logic. 🚀
        throttle = int(keys[pygame.K_UP])  # ⬆️ accelerate
        brake = int(keys[pygame.K_DOWN])  # ⬇️ slow down
        if self.disable_brake:
            brake = 0

        # Steering uses arrow keys.
        steer = 0.0
        if keys[pygame.K_LEFT]:  # ⬅️ turn left
            steer -= 1.0
        if keys[pygame.K_RIGHT]:  # ➡️ turn right
            steer += 1.0

        # Simple gear shifting with Z/X. 🔧
        gear = 0
        shift_up = keys[pygame.K_x]  # X to shift up
        shift_down = keys[pygame.K_z]  # Z to shift down
        if shift_up and not self._last_up:
            gear = 1
        if shift_down and not self._last_down:
            gear = -1
        self._last_up = shift_up
        self._last_down = shift_down

        return {
            "throttle": throttle,
            "brake": brake,
            "steer": steer,
            "gear": gear,
        }
