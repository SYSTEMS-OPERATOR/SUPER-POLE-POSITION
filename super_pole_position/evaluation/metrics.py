#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 MIND INTERFACES, INC. All rights reserved.
# Licensed under the MIT License.

"""
metrics.py
Description: Module for Super Pole Position.
"""


from __future__ import annotations

from typing import Any, Dict, List


def summary(env: Any) -> Dict[str, float | int | None]:
    """Extract metrics from ``env`` for leaderboard."""
    return {
        "reward": getattr(env, "episode_reward", 0.0),
        "qualifying_time": getattr(env, "qualifying_time", None),
        "passes": getattr(env, "passes", 0),
        "crashes": getattr(env, "crashes", 0),
        "gear_shifts": env.cars[0].shift_count if env.cars else 0,
        "ai_offtrack": getattr(env, "ai_offtrack", 0),
        "avg_plan_ms": (
            1000.0 * sum(env.plan_durations) / len(env.plan_durations)
            if getattr(env, "plan_durations", [])
            else 0.0
        ),
        "avg_step_ms": (
            1000.0 * sum(env.step_durations) / len(env.step_durations)
            if getattr(env, "step_durations", [])
            else 0.0
        ),
        "tokens": sum(getattr(env, "plan_tokens", [])),
    }


def lap_time(rewards: List[float]) -> float:
    """Compute pseudo lap time as inverse of total reward."""
    return 1.0 / max(sum(rewards), 1e-6)
