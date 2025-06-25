
import os
import subprocess
import sys
import venv
from pathlib import Path

import pytest

@pytest.mark.timeout(30)

def test_wheel_smoke(tmp_path):
    wheel_dir = tmp_path / "wheel"
    wheel_dir.mkdir()
    subprocess.check_call([sys.executable, "-m", "pip", "wheel", ".", "-w", str(wheel_dir)])
    wheel = next(wheel_dir.glob("super_pole_position-*.whl"))
    venv_dir = tmp_path / "venv"
    subprocess.check_call([sys.executable, "-m", "venv", str(venv_dir)])
    pip = venv_dir / "bin" / "pip"
    exe = venv_dir / "bin" / "super-pole-position"
    subprocess.check_call([str(pip), "install", str(wheel)])
    env = {"FAST_TEST": "1", "SDL_VIDEODRIVER": "dummy", **os.environ}
    subprocess.check_call([str(exe), "race", "--agent", "null"], env=env)

