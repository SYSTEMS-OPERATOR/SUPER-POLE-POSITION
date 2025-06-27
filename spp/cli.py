import argparse
import os
from super_pole_position.log_utils import init_playtest_logger
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
    race.add_argument("--release", action="store_true")

    def _installed_via_wheel() -> bool:
        from pathlib import Path

        return "site-packages" in Path(__file__).resolve().parts

    args = parser.parse_args()
    if not getattr(args, "release", False) and _installed_via_wheel():
        args.release = True
    if getattr(args, "headless", False):
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        os.environ.setdefault("FAST_TEST", "1")

    if getattr(args, "release", False) or os.getenv("ENV") == "production":
        os.environ["SPP_RELEASE"] = "1"
        os.environ["PERF_HUD"] = "0"
        os.environ["AUDIO"] = "1"
        os.environ.setdefault("WINDOW_W", "1280")
        os.environ.setdefault("WINDOW_H", "720")
        os.environ.setdefault("VSYNC", "1")
        init_playtest_logger()

    env = PolePositionEnv(render_mode="human", mode_2600=getattr(args, "mode_2600", False))
    env.reset(seed=getattr(args, "seed", 0))
    for _ in range(getattr(args, "steps", 3)):
        env.step({"throttle": False, "brake": False, "steer": 0.0})
    env.close()


if __name__ == "__main__":  # pragma: no cover - CLI
    main()
