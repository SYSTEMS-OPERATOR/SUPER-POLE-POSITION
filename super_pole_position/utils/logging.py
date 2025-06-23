"""Logging helpers for SUPER-POLE-POSITION."""

from __future__ import annotations

from typing import Tuple

from ..agents.base_llm_agent import BaseLLMAgent
from ..envs.pole_position import PolePositionEnv
from ..matchmaking.arena import run_episode


def safe_run_episode(env: PolePositionEnv, agents: Tuple[BaseLLMAgent, BaseLLMAgent]) -> None:
    """Run an episode and log any exception."""
    try:
        run_episode(env, agents)
    except Exception as exc:  # pragma: no cover - defensive
        print(f"episode error: {exc}", flush=True)

