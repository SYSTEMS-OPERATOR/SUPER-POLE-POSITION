import argparse
from pathlib import Path
import shutil
import zipfile


def main(dest: str) -> None:
    dest_path = Path(dest)
    dest_path.mkdir(parents=True, exist_ok=True)
    zip_path = dest_path / "spp_playtest.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.write("run_game.py")
        for file in Path("assets").rglob("*"):
            if file.is_file():
                zf.write(file)
    print(f"Created {zip_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dest", default="build/playtest_zip")
    args = parser.parse_args()
    main(args.dest)
