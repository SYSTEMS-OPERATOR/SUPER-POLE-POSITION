#!/usr/bin/env python3

"""Launch the game with one press. 🕹️✨"""


from __future__ import annotations

from super_pole_position.agents.keyboard_agent import KeyboardAgent
from super_pole_position.envs.pole_position import PolePositionEnv
from super_pole_position.evaluation.metrics import summary
from super_pole_position.matchmaking.arena import run_episode


INTRO = """
 rrr
rrrrr
 rrr
🚥  READY?
"""


def main() -> None:
    """Show a tiny intro and jump into the race. 🏁"""

    # 🚦 Display the game title
    print("🏎️ SUPER-POLE-POSITION 🏁")
    print(INTRO)


    # ⏱️ Wait for the player to begin
    input("Press Enter to start!")

    # 🎮 Create the environment and keyboard agent
    # 🚗 Prepare the track and cars
    # Create a race-ready environment. 🏆

    env = PolePositionEnv(render_mode="human", mode="race", track_name="fuji")
    # KeyboardAgent lets you take control of the action. 🎮
    agent = KeyboardAgent()

    # 🏎️ Run a single race where both cars share the same agent
    # 🔁 One quick lap with two identical agents

    run_episode(env, (agent, agent))
    # 📊 Display a tiny summary

    print(summary(env))
    print("🎉 Thanks for playing!")
    env.close()


if __name__ == "__main__":  # pragma: no cover - manual launch
    main()
