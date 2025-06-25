#!/usr/bin/env python3
"""Module entry point for ``python -m spp``."""

from __future__ import annotations

import argparse
import sys

from .cli import main as cli_main
from .envs.pole_position import PolePositionEnv


def _smoke_run(steps: int) -> None:
    """Run a minimal headless episode for smoke tests."""

    env = PolePositionEnv(render_mode="human")
    env.reset(seed=0)
    for _ in range(steps):
        env.step({"throttle": False, "brake": False, "steer": 0.0})
    env.close()


def main(argv: list[str] | None = None) -> None:
    """Handle ``--headless`` or dispatch to CLI."""

    parser = argparse.ArgumentParser(prog="spp")
    parser.add_argument("--headless", action="store_true", help="Run without UI")
    parser.add_argument("--steps", type=int, default=3, help="Steps for smoke run")
    args, extra = parser.parse_known_args(argv)

    if args.headless:
        _smoke_run(args.steps)
    else:
        sys.argv = [sys.argv[0]] + extra
        cli_main()


if __name__ == "__main__":  # pragma: no cover - manual launch
    main()
