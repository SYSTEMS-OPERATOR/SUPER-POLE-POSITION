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
from typing import Optional

from .log_utils import init_playtest_logger

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


def _installed_via_wheel() -> bool:
    """Return ``True`` when this module is loaded from a wheel install."""

    return "site-packages" in Path(__file__).resolve().parts


def _configure_runtime_flags(args: argparse.Namespace) -> None:
    """Configure environment flags based on CLI options."""

    if not args.release and _installed_via_wheel():
        args.release = True
    if args.release or os.getenv("ENV") == "production":
        os.environ["SPP_RELEASE"] = "1"
        os.environ["PERF_HUD"] = "0"
        os.environ["AUDIO"] = "1"
        os.environ.setdefault("WINDOW_W", "1280")
        os.environ.setdefault("WINDOW_H", "720")
        os.environ.setdefault("VSYNC", "1")
        init_playtest_logger()
    if args.upload:
        os.environ["SPP_UPLOAD"] = "1"

    # 🧭 Dev Agent Breadcrumb: normalize menu/game toggles before dispatch.
    os.environ["MUTE_BGM"] = "1" if getattr(args, "mute_bgm", False) else "0"
    os.environ["VIRTUAL_JOYSTICK"] = (
        "1" if getattr(args, "virtual_joystick", False) else "0"
    )
    os.environ["DISABLE_BRAKE"] = "1" if getattr(args, "no_brake", False) else "0"
    os.environ["ATTRACT_MODE"] = "1" if getattr(args, "attract_mode", False) else "0"


def _launch_menu_if_requested(args: argparse.Namespace) -> Optional[dict]:
    """Open the in-game menu for rendered runs and return selected options."""

    if not getattr(args, "render", False):
        return None

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
        return menu.main_loop(screen)
    except Exception:
        return None
    finally:
        pygame.quit()


def _apply_menu_config(args: argparse.Namespace, cfg: Optional[dict]) -> bool:
    """Apply menu overrides to ``args``. Return ``False`` on canceled menu."""

    if cfg is None:
        return not getattr(args, "render", False)

    args.track = cfg.get("track", args.track)
    args.difficulty = cfg.get("difficulty", args.difficulty)
    os.environ["AUDIO"] = "1" if cfg.get("audio", True) else "0"
    return True


def _run_game_mode(args: argparse.Namespace, mode: str) -> None:
    """Run either ``qualify`` or ``race`` mode."""

    cfg = _launch_menu_if_requested(args)
    if not _apply_menu_config(args, cfg):
        return

    # 🧭 Dev Agent Breadcrumb: environment + agent setup.
    env = PolePositionEnv(
        render_mode="human",
        mode=mode,
        track_name=args.track,
        track_file=args.track_file,
        player_name=args.player,
        difficulty=args.difficulty,
        start_position=getattr(args, "start_pos", None),
    )
    agent_cls = AGENT_MAP.get(args.agent, NullAgent)
    agent = agent_cls()

    # 🧭 Dev Agent Breadcrumb: run episode, record leaderboard, persist score.
    safe_run_episode(env, (agent, agent))
    metrics = summary(env)
    update_leaderboard(
        Path(__file__).parent / "evaluation" / "leaderboard.json",
        f"{args.agent}-{mode}",
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


def _handle_utility_commands(args: argparse.Namespace) -> bool:
    """Handle non-racing CLI commands and return ``True`` if handled."""

    if args.cmd == "hiscore":
        score_file = Path(__file__).parent / "evaluation" / "scores.json"
        scores = load_scores(score_file)
        for index, score in enumerate(scores, 1):
            print(f"{index:2d}. {score['name']} {score['score']}")
        return True
    if args.cmd == "reset-scores":
        answer = input("Reset all scores? [y/N]: ")
        if answer.lower().startswith("y"):
            reset_scores(Path(__file__).parent / "evaluation" / "scores.json")
        return True
    if args.cmd == "scoreboard-sync":
        from .server import sync

        sync.start_service(args.host, args.port, args.interval)
        return True
    return False


def main() -> None:
    """Entry point for the ``super-pole-position`` command line interface."""

    parser = argparse.ArgumentParser(prog="spp")
    parser.add_argument("--release", action="store_true")
    parser.add_argument("--upload", action="store_true")
    sub = parser.add_subparsers(dest="cmd")
    q = sub.add_parser("qualify")
    q.add_argument("--agent", choices=list(AGENT_MAP.keys()), default="keyboard")
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
    r.add_argument("--agent", choices=list(AGENT_MAP.keys()), default="keyboard")
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
    _configure_runtime_flags(args)
    if _handle_utility_commands(args):
        return

    if args.cmd == "qualify":
        _run_game_mode(args, "qualify")
        return

    _run_game_mode(args, "race")


if __name__ == "__main__":
    main()
