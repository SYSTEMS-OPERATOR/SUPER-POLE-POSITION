import argparse
import os
from super_pole_position.envs.pole_position import PolePositionEnv


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--steps", type=int, default=3)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--2600-mode", dest="mode_2600", action="store_true")
    args = parser.parse_args()

    if args.headless:
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        os.environ.setdefault("FAST_TEST", "1")

    env = PolePositionEnv(render_mode="human", mode_2600=args.mode_2600)
    env.reset(seed=args.seed)
    for _ in range(args.steps):
        env.step({"throttle": False, "brake": False, "steer": 0.0})
    env.close()


if __name__ == "__main__":  # pragma: no cover - CLI
    main()
