#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 MIND INTERFACES, INC. All rights reserved.
# Licensed under the MIT License.

"""
base_llm_agent.py
Description: Module for Super Pole Position.
"""


from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseLLMAgent(ABC):
    """Common interface for LLM-driven agents."""

    @abstractmethod
    def act(self, observation: Any) -> Dict[str, float]:
        """Return an action dict given an observation."""


class NullAgent(BaseLLMAgent):
    """Heuristic agent used for offline tests."""

    def act(self, observation: Any) -> Dict[str, float]:
        """Return a simple throttle/brake policy for baseline testing."""

        # Simple policy: throttle until half max speed, no steering
        speed = observation[2]
        throttle = speed < 5.0
        return {
            "throttle": float(throttle),
            "brake": float(not throttle),
            "steer": 0.0,
            "gear": 0.0,
        }
