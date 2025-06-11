from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Tuple

from ..envs.pole_position import PolePositionEnv
from ..agents.base_llm_agent import BaseLLMAgent


def run_episode(env: PolePositionEnv, agents: Tuple[BaseLLMAgent, BaseLLMAgent]) -> float:
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
    return total


def update_leaderboard(file: Path, name: str, metrics: dict) -> None:
    data = {"schema_version": 2, "results": []}
    if file.exists():
        data = json.loads(file.read_text())
    entry = {"name": name}
    entry.update(metrics)
    data["results"].append(entry)
    data["results"] = sorted(data["results"], key=lambda r: -r.get("reward", 0))[:10]
    file.write_text(json.dumps(data, indent=2))
