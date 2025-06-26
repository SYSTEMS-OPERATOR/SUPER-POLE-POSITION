import argparse
import os
from super_pole_position.envs.pole_position import PolePositionEnv


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd")

    race = sub.add_parser("race")
    race.add_argument("--agent", default="null")
    race.add_argument("--headless", action="store_true")
    race.add_argument("--steps", type=int, default=3)
    race.add_argument("--seed", type=int, default=0)
    race.add_argument("--2600-mode", dest="mode_2600", action="store_true")

    args = parser.parse_args()
    if getattr(args, "headless", False):
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        os.environ.setdefault("FAST_TEST", "1")

    env = PolePositionEnv(render_mode="human", mode_2600=getattr(args, "mode_2600", False))
    env.reset(seed=getattr(args, "seed", 0))
    for _ in range(getattr(args, "steps", 3)):
        env.step({"throttle": False, "brake": False, "steer": 0.0})
    env.close()


if __name__ == "__main__":  # pragma: no cover - CLI
    main()
