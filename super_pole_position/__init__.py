#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 MIND INTERFACES, INC. All rights reserved.
# Licensed under the MIT License.

"""
__init__.py
Description: Module for Super Pole Position.
"""

import os

# Hide pygame's greeting for cleaner logs
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

# Ensure pygame can initialise even without a display
if os.name != "nt" and "DISPLAY" not in os.environ:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")



from .physics.car import Car
from .physics.track import Track
from .envs.pole_position import PolePositionEnv
from .agents.controllers import (
    GPTPlanner,
    LowLevelController,
    LearningAgent,
)
from .agents.base_llm_agent import BaseLLMAgent, NullAgent

__all__ = [
    "Car",
    "Track",
    "PolePositionEnv",
    "GPTPlanner",
    "LowLevelController",
    "LearningAgent",
    "BaseLLMAgent",
    "NullAgent",
]
