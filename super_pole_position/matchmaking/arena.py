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
from typing import Any, Dict, Tuple

from ..envs.pole_position import PolePositionEnv
from ..agents.base_llm_agent import BaseLLMAgent


def run_episode(
    env: PolePositionEnv, agents: Tuple[BaseLLMAgent, BaseLLMAgent]
) -> float:
    """Run one episode and return cumulative reward for agent 0."""
    obs, _ = env.reset()
    if env.render_mode == "human":
        try:
            env.render()
        except Exception as exc:
            print(f"render error: {exc}", flush=True)
    done = False
    total = 0.0
    while not done:
        if env.render_mode == "human":
            try:
                env.render()
            except Exception as exc:
                print(f"render error: {exc}", flush=True)
        try:
            action0 = agents[0].act(obs)
        except Exception as exc:
            print(f"agent error: {exc}", flush=True)
            action0 = {}
        action0_tuple = (
            action0.get("throttle", 0),
            action0.get("brake", 0),
            action0.get("steer", 0.0),
            action0.get("gear", 0),
        )
        try:
            obs, reward, done, _, _ = env.step(action0_tuple)
        except Exception as exc:
            print(f"step error: {exc}", flush=True)
            break
        total += reward
        if env.render_mode == "human":
            try:
                env.render()
            except Exception as exc:
                print(f"render error: {exc}", flush=True)
    env.episode_reward = total
    return total


def update_leaderboard(
    file: Path, name: str, metrics: Dict[str, float | int | None]
) -> None:
    """Append ``metrics`` for ``name`` to ``file`` in leaderboard format."""

    data: Dict[str, Any] = {"schema_version": 2, "results": []}
    if file.exists():
        data = json.loads(file.read_text())

    entry: Dict[str, Any] = {"name": name}
    entry.update(metrics)

    results: list[Dict[str, Any]] = data.get("results", [])
    results.append(entry)
    data["results"] = sorted(results, key=lambda r: -float(r.get("reward", 0)))[:10]
    file.write_text(json.dumps(data, indent=2))
