from __future__ import annotations

import argparse
from pathlib import Path

from .agents.base_llm_agent import NullAgent
from .envs.pole_position import PolePositionEnv
from .matchmaking.arena import run_episode, update_leaderboard


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", type=int, default=1)
    args = parser.parse_args()

    env = PolePositionEnv(render_mode="human")
    agent = NullAgent()
    for ep in range(args.episodes):
        reward = run_episode(env, (agent, agent))
        update_leaderboard(Path(__file__).parent / "evaluation" / "leaderboard.json", f"NullAgent-{ep}", reward)
        print(f"Episode {ep} reward {reward:.2f}")


if __name__ == "__main__":
    main()
