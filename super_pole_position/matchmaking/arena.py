#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 MIND INTERFACES, INC. All rights reserved.
# Licensed under the MIT License.

"""
arena.py
Description: Module for Super Pole Position.
"""


from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Tuple

from ..envs.pole_position import PolePositionEnv
from ..agents.base_llm_agent import BaseLLMAgent


def run_episode(
    env: PolePositionEnv, agents: Tuple[BaseLLMAgent, BaseLLMAgent]
) -> float:
    """Run one episode and return cumulative reward for agent 0."""
    obs, _ = env.reset()
    done = False
    total = 0.0
    while not done:
        action0 = agents[0].act(obs)
        action0_tuple = (
            action0.get("throttle", 0),
            action0.get("brake", 0),
            action0.get("steer", 0.0),
            action0.get("gear", 0),
        )
        obs, reward, done, _, _ = env.step(action0_tuple)
        total += reward
    env.episode_reward = total
    date_dir = Path("benchmarks") / datetime.now(timezone.utc).strftime("%Y-%m-%d")
    date_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%H%M%S")
    out = {
        "agent": getattr(agents[0], "name", "agent"),
        "track": getattr(env, "track_name", "unknown"),
        "result": {"reward": total},
        "perf": {"steps": env.current_step},
    }
    (date_dir / f"{ts}.json").write_text(json.dumps(out, indent=2))
    return total


def update_leaderboard(file: Path, name: str, metrics: dict) -> None:
    """Append ``metrics`` for ``name`` to ``file`` in leaderboard format."""

    data = {"schema_version": 2, "results": []}
    if file.exists():
        data = json.loads(file.read_text())
    entry = {"name": name}
    entry.update(metrics)
    data["results"].append(entry)
    data["results"] = sorted(data["results"], key=lambda r: -r.get("reward", 0))[:10]
    file.write_text(json.dumps(data, indent=2))
