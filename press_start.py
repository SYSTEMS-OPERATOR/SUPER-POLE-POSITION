#!/usr/bin/env python3
"""Launch the game with one press. 🕹️"""

from __future__ import annotations

from super_pole_position.agents.keyboard_agent import KeyboardAgent
from super_pole_position.envs.pole_position import PolePositionEnv
from super_pole_position.evaluation.metrics import summary
from super_pole_position.matchmaking.arena import run_episode


INTRO = """
 rrr
rrrrr
 rrr
"""


def main() -> None:
    """Show a tiny intro and jump into the race."""

    print("🏎️ SUPER-POLE-POSITION 🏁")
    print(INTRO)
    input("Press Enter to start!")
    env = PolePositionEnv(render_mode="human", mode="race", track_name="fuji")
    agent = KeyboardAgent()
    run_episode(env, (agent, agent))
    print(summary(env))
    env.close()


if __name__ == "__main__":  # pragma: no cover - manual launch
    main()
