#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 MIND INTERFACES, INC. All rights reserved.
# Licensed under the MIT License.

"""
cli.py
Description: Module for Super Pole Position.
"""


from __future__ import annotations

import argparse
import os
from pathlib import Path

from .agents.base_llm_agent import NullAgent
from .agents.openai_agent import OpenAIAgent
from .agents.mistral_agent import MistralAgent
from .agents.keyboard_agent import KeyboardAgent
from .agents.joystick_agent import JoystickAgent

from .envs.pole_position import PolePositionEnv, FAST_TEST
from .matchmaking.arena import run_episode as _run_episode, update_leaderboard
from .utils import safe_run_episode
from .evaluation.metrics import summary
from .evaluation.scores import load_scores, reset_scores, update_scores
from .ui.menu import show_race_outro

AGENT_MAP = {
    "null": NullAgent,
    "openai": OpenAIAgent,
    "mistral": MistralAgent,
    "keyboard": KeyboardAgent,
    "joystick": JoystickAgent,
}


def run_episode(env: PolePositionEnv, agents) -> None:
    """Compatibility wrapper invoking arena.run_episode."""
    _run_episode(env, agents)


def main() -> None:
    """Entry point for the ``super-pole-position`` command line interface."""

    parser = argparse.ArgumentParser(prog="spp")
    sub = parser.add_subparsers(dest="cmd")
    q = sub.add_parser("qualify")
    q.add_argument("--agent", choices=list(AGENT_MAP.keys()), default="null")
    q.add_argument("--track", default="fuji")
    q.add_argument("--track-file", dest="track_file")
    q.add_argument("--render", action="store_true")
    q.add_argument("--mute-bgm", action="store_true", help="Disable background music")
    q.add_argument("--player", default="PLAYER", help="Name for score entry")
    q.add_argument(
        "--virtual-joystick",
        action="store_true",
        help="Enable on-screen controls for touch devices",
    )
    q.add_argument(
        "--no-brake",
        action="store_true",
        help="Disable brake input for purist mode",
    )
    q.add_argument(
        "--difficulty",
        choices=["beginner", "expert"],
        default="beginner",
        help="Set difficulty level for time limits",
    )
    q.add_argument(
        "--attract-mode",
        action="store_true",
        help="Cycle leaderboard when idle at menu",
    )

    r = sub.add_parser("race")
    r.add_argument("--agent", choices=list(AGENT_MAP.keys()), default="null")
    r.add_argument("--track", default="fuji")
    r.add_argument("--track-file", dest="track_file")
    r.add_argument("--render", action="store_true")
    r.add_argument("--mute-bgm", action="store_true", help="Disable background music")
    r.add_argument("--player", default="PLAYER", help="Name for score entry")
    r.add_argument(
        "--virtual-joystick",
        action="store_true",
        help="Enable on-screen controls for touch devices",
    )
    r.add_argument(
        "--no-brake",
        action="store_true",
        help="Disable brake input for purist mode",
    )
    r.add_argument(
        "--difficulty",
        choices=["beginner", "expert"],
        default="beginner",
        help="Set difficulty level for time limits",
    )
    r.add_argument(
        "--start-pos",
        type=int,
        help="Grid position from qualifying",
    )  
    r.add_argument(
        "--attract-mode",
        action="store_true",
        help="Cycle leaderboard when idle at menu",
    )

    sub.add_parser("hiscore")
    sub.add_parser("reset-scores")
    s = sub.add_parser("scoreboard-sync")
    s.add_argument("--host", default="127.0.0.1")
    s.add_argument("--port", type=int, default=8000)
    s.add_argument("--interval", type=float, default=60.0)
    args = parser.parse_args()
    if getattr(args, "mute_bgm", False):
        os.environ["MUTE_BGM"] = "1"
    else:
        os.environ.setdefault("MUTE_BGM", "0")
    if getattr(args, "virtual_joystick", False):
        os.environ["VIRTUAL_JOYSTICK"] = "1"
    else:
        os.environ.setdefault("VIRTUAL_JOYSTICK", "0")
    if getattr(args, "no_brake", False):
        os.environ["DISABLE_BRAKE"] = "1"
    else:
        os.environ.setdefault("DISABLE_BRAKE", "0")
    if getattr(args, "attract_mode", False):
        os.environ["ATTRACT_MODE"] = "1"
    else:
        os.environ.setdefault("ATTRACT_MODE", "0")

    if args.cmd == "hiscore":
        file = Path(__file__).parent / "evaluation" / "scores.json"
        scores = load_scores(file)
        for i, s in enumerate(scores, 1):
            print(f"{i:2d}. {s['name']} {s['score']}")
        return
    if args.cmd == "reset-scores":
        answer = input("Reset all scores? [y/N]: ")
        if answer.lower().startswith("y"):
            reset_scores(Path(__file__).parent / "evaluation" / "scores.json")
        return
    if args.cmd == "scoreboard-sync":
        from .server import sync

        sync.start_service(args.host, args.port, args.interval)
        return

    if args.cmd == "qualify":
        if args.render:
            if os.name != "nt" and "DISPLAY" not in os.environ:
                os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
            try:
                import pygame
                from .ui import menu
            except Exception:  # noqa: E402 - optional dependency
                print("pygame required for --render", flush=True)
                raise SystemExit(1)

            pygame.init()
            screen = pygame.display.set_mode((256, 224))
            try:
                cfg = menu.main_loop(screen)
            except Exception:
                cfg = None
            pygame.quit()
            if cfg is None:
                return
            args.track = cfg.get("track", args.track)
            args.difficulty = cfg.get("difficulty", args.difficulty)
            os.environ["AUDIO"] = "1" if cfg.get("audio", True) else "0"
        env = PolePositionEnv(
            render_mode="human",
            mode="qualify",
            track_name=args.track,
            track_file=args.track_file,
            player_name=args.player,
            difficulty=args.difficulty,
        )
        agent_cls = AGENT_MAP.get(args.agent, NullAgent)
        agent = agent_cls()
        safe_run_episode(env, (agent, agent))
        metrics = summary(env)
        update_leaderboard(
            Path(__file__).parent / "evaluation" / "leaderboard.json",
            f"{args.agent}-qualify",
            metrics,
        )
        update_scores(
            Path(__file__).parent / "evaluation" / "scores.json",
            args.player,
            int(env.score),
        )
        try:
            show_race_outro(
                getattr(env, "screen", None),
                int(env.score),
                duration=0 if FAST_TEST else 5.0,
            )
        except Exception:
            pass
        env.close()
        print(metrics)
    else:
        if args.render:
            if os.name != "nt" and "DISPLAY" not in os.environ:
                os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
            try:
                import pygame
                from .ui import menu
            except Exception:  # noqa: E402 - optional dependency
                print("pygame required for --render", flush=True)
                raise SystemExit(1)

            pygame.init()
            screen = pygame.display.set_mode((256, 224))
            try:
                cfg = menu.main_loop(screen)
            except Exception:
                cfg = None
            pygame.quit()
            if cfg is None:
                return
            args.track = cfg.get("track", args.track)
            args.difficulty = cfg.get("difficulty", args.difficulty)
            os.environ["AUDIO"] = "1" if cfg.get("audio", True) else "0"
        env = PolePositionEnv(
            render_mode="human",
            mode="race",
            track_name=args.track,
            track_file=args.track_file,
            player_name=args.player,
            difficulty=args.difficulty,
            start_position=args.start_pos,
        )
        agent_cls = AGENT_MAP.get(args.agent, NullAgent)
        agent = agent_cls()
        safe_run_episode(env, (agent, agent))
        metrics = summary(env)
        update_leaderboard(
            Path(__file__).parent / "evaluation" / "leaderboard.json",
            f"{args.agent}-race",
            metrics,
        )
        update_scores(
            Path(__file__).parent / "evaluation" / "scores.json",
            args.player,
            int(env.score),
        )
        try:
            show_race_outro(
                getattr(env, "screen", None),
                int(env.score),
                duration=0 if FAST_TEST else 5.0,
            )
        except Exception:
            pass
        env.close()
        print(metrics)


if __name__ == "__main__":
    main()
