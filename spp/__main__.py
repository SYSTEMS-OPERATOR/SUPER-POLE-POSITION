import argparse
import os
import sys
from super_pole_position.envs.pole_position import PolePositionEnv


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--steps", type=int, default=3)
    args = parser.parse_args()

    if args.headless:
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        os.environ.setdefault("FAST_TEST", "1")

    env = PolePositionEnv(render_mode="human")
    env.reset(seed=0)
    for _ in range(args.steps):
        env.step({"throttle": False, "brake": False, "steer": 0.0})
    env.close()


if __name__ == "__main__":  # pragma: no cover - CLI
    main()
