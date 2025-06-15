#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
keyboard_agent.py
Description: Module for Super Pole Position.
"""

from __future__ import annotations

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

    def act(self, observation) -> dict:
        if pygame is None:
            return {"throttle": 0, "brake": 0, "steer": 0.0, "gear": 0}

        keys = pygame.key.get_pressed()
        throttle = int(keys[pygame.K_UP])
        brake = int(keys[pygame.K_DOWN])
        steer = 0.0
        if keys[pygame.K_LEFT]:
            steer -= 1.0
        if keys[pygame.K_RIGHT]:
            steer += 1.0

        gear = 0
        shift_up = keys[pygame.K_x]
        shift_down = keys[pygame.K_z]
        if shift_up and not self._last_up:
            gear = 1
        if shift_down and not self._last_down:
            gear = -1
        self._last_up = shift_up
        self._last_down = shift_down
        return {"throttle": throttle, "brake": brake, "steer": steer, "gear": gear}
