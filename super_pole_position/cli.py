from __future__ import annotations

import argparse
from pathlib import Path

from .agents.base_llm_agent import NullAgent
from .envs.pole_position import PolePositionEnv
from .matchmaking.arena import run_episode, update_leaderboard
from .evaluation.metrics import summary


def main() -> None:
    parser = argparse.ArgumentParser(prog="spp")
    sub = parser.add_subparsers(dest="cmd")
    q = sub.add_parser("qualify")
    q.add_argument("--agent", default="null")
    q.add_argument("--track", default="fuji")
    r = sub.add_parser("race")
    r.add_argument("--agent", default="null")
    r.add_argument("--track", default="fuji")
    args = parser.parse_args()

    if args.cmd == "qualify":
        env = PolePositionEnv(render_mode="human", mode="qualify", track_name=args.track)
        agent = NullAgent()
        run_episode(env, (agent, agent))
        metrics = summary(env)
        update_leaderboard(Path(__file__).parent / "evaluation" / "leaderboard.json", f"{args.agent}-qualify", metrics)
        env.close()
        print(metrics)
    else:
        env = PolePositionEnv(render_mode="human", mode="race", track_name=args.track)
        agent = NullAgent()
        run_episode(env, (agent, agent))
        metrics = summary(env)
        update_leaderboard(Path(__file__).parent / "evaluation" / "leaderboard.json", f"{args.agent}-race", metrics)
        env.close()
        print(metrics)


if __name__ == "__main__":
    main()
