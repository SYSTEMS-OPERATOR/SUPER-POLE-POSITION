#!/usr/bin/env python3
"""Create standalone playtest zip."""

import argparse
import shutil
import zipfile
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dest", required=True)
    args = parser.parse_args()

    dest = Path(args.dest)
    dest.mkdir(parents=True, exist_ok=True)
    zip_path = dest / "super_pole_position_playtest.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.write("run_game.py")
        for path in Path("assets").rglob("*"):
            if path.is_file():
                zf.write(path, path.as_posix())
    print(f"Wrote {zip_path}")


if __name__ == "__main__":
    main()
