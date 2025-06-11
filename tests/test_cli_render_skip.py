import subprocess
import sys


def test_cli_render_skip(monkeypatch):
    monkeypatch.setitem(sys.modules, "pygame", None)
    result = subprocess.run(
        [sys.executable, "-m", "super_pole_position.cli", "race", "--render"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert result.returncode == 1
