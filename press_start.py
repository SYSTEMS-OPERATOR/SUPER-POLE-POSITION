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
    # Wait for the player to start – retro style! ✨
    input("Press Enter to start! 🎉")
    # Create a race-ready environment. 🏆
    env = PolePositionEnv(render_mode="human", mode="race", track_name="fuji")
    # KeyboardAgent lets you take control of the action. 🎮
    agent = KeyboardAgent()
    # Run a single episode with our agent versus itself. 🤖
    run_episode(env, (agent, agent))
    # Print a quick metrics summary. 📊
    print(summary(env))
    env.close()


if __name__ == "__main__":  # pragma: no cover - manual launch
    main()
