import os
import sys
import subprocess


def test_cli_smoke() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "spp", "--headless", "--steps", "3"],
        env={**os.environ, "SDL_VIDEODRIVER": "dummy"},
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=5,
    )
    assert result.returncode == 0
