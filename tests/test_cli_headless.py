import subprocess
import sys


def test_cli_headless():
    result = subprocess.run(
        [sys.executable, "-m", "super_pole_position.cli", "race"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert result.returncode == 0
