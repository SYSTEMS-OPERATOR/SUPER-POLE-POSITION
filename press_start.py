#!/usr/bin/env python3

"""Launch the game with one press. 🕹️✨"""


from __future__ import annotations

from super_pole_position.agents.keyboard_agent import KeyboardAgent
from super_pole_position.envs.pole_position import PolePositionEnv
from super_pole_position.evaluation.metrics import summary
from super_pole_position.matchmaking.arena import run_episode
import logging


INTRO = """
 rrr
rrrrr
 rrr
🚥  READY?

Press 'M' in-game to load the GPT model.
"""


def main() -> None:
    """Show a tiny intro and jump into the race. 🏁"""

    logging.basicConfig(level=logging.INFO)

    # 🚦 Display the game title
    print("🏎️ SUPER-POLE-POSITION 🏁")
    print(INTRO)

    # ⏱️ Wait for the player to begin
    input("Press Enter to start!")

    env: PolePositionEnv | None = None
    try:
        # 🎮 Create the environment and keyboard agent
        # 🚗 Prepare the track and cars
        env = PolePositionEnv(render_mode="human", mode="race", track_name="fuji")
        agent = KeyboardAgent()  # Take control of the action. 🎮

        # 🔁 Allow multiple races without closing the window
        play_again = True
        while play_again:
            env.reset()
            run_episode(env, (agent, agent))
            print(summary(env))
            ans = input("Race again? [y/N] ")
            play_again = ans.strip().lower().startswith("y")

        print("🎉 Thanks for playing!")
    except Exception as exc:  # pragma: no cover - manual error handler
        logging.exception("Game crashed: %s", exc)
    finally:
        if env is not None:
            env.close()


if __name__ == "__main__":  # pragma: no cover - manual launch
    main()
