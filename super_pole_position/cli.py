from __future__ import annotations

import argparse
from pathlib import Path

from .agents.base_llm_agent import NullAgent
from .envs.pole_position import PolePositionEnv
from .matchmaking.arena import run_episode, update_leaderboard
from .evaluation.metrics import summary
from .evaluation.scores import load_scores, update_scores, reset_scores


def main() -> None:
    parser = argparse.ArgumentParser(prog="spp")
    sub = parser.add_subparsers(dest="cmd")
    q = sub.add_parser("qualify")
    q.add_argument("--agent", default="null")
    q.add_argument("--track", default="fuji")

    r = sub.add_parser("race")
    r.add_argument("--agent", default="null")
    r.add_argument("--track", default="fuji")

    sub.add_parser("hiscore")
    sub.add_parser("reset-scores")
    args = parser.parse_args()

    if args.cmd == "hiscore":
        file = Path(__file__).parent / "evaluation" / "scores.json"
        scores = load_scores(file)
        for i, s in enumerate(scores, 1):
            print(f"{i:2d}. {s['name']} {s['score']}")
        return
    if args.cmd == "reset-scores":
        ans = input("Reset all scores? [y/N]: ")
        if ans.lower().startswith("y"):
            reset_scores(Path(__file__).parent / "evaluation" / "scores.json")
        return

    if args.cmd == "qualify":
        env = PolePositionEnv(render_mode="human", mode="qualify", track_name=args.track)
        agent = NullAgent()
        run_episode(env, (agent, agent))
        metrics = summary(env)
        update_leaderboard(Path(__file__).parent / "evaluation" / "leaderboard.json", f"{args.agent}-qualify", metrics)
        update_scores(Path(__file__).parent / "evaluation" / "scores.json", args.agent, int(env.score))
        env.close()
        print(metrics)
    else:
        env = PolePositionEnv(render_mode="human", mode="race", track_name=args.track)
        agent = NullAgent()
        run_episode(env, (agent, agent))
        metrics = summary(env)
        update_leaderboard(Path(__file__).parent / "evaluation" / "leaderboard.json", f"{args.agent}-race", metrics)
        update_scores(Path(__file__).parent / "evaluation" / "scores.json", args.agent, int(env.score))
        env.close()
        print(metrics)


if __name__ == "__main__":
    main()
