import subprocess
import sys


def test_cli_stub():
    result = subprocess.run(
        [sys.executable, "-m", "spp", "--headless", "--steps", "3"],
        timeout=5,
    )
    assert result.returncode == 0
