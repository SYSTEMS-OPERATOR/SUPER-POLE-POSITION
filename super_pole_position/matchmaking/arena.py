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
        action0_tuple = (action0["throttle"], action0["brake"], action0["steer"])
        obs, reward, done, _, _ = env.step(action0_tuple)
        total += reward
    env.close()
    return total


def update_leaderboard(file: Path, name: str, reward: float) -> None:
    data = {"results": []}
    if file.exists():
        data = json.loads(file.read_text())
    data["results"].append({"name": name, "reward": reward})
    data["results"] = sorted(data["results"], key=lambda r: -r["reward"])[:10]
    file.write_text(json.dumps(data, indent=2))
