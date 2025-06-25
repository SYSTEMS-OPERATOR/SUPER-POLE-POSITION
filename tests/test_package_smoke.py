import subprocess
import sys
import venv


import pytest


@pytest.mark.timeout(30)
def test_wheel_smoke(tmp_path):
    wheel_dir = tmp_path / "wheel"
    wheel_dir.mkdir()
    subprocess.check_call([sys.executable, "-m", "pip", "wheel", ".", "-w", str(wheel_dir)])
    env_dir = tmp_path / "venv"
    venv.EnvBuilder(with_pip=True).create(env_dir)
    exe = env_dir / "bin" / "pip"
    all_wheels = sorted(str(p) for p in wheel_dir.glob("*.whl"))
    subprocess.check_call([str(exe), "install", "--no-index", "--find-links", str(wheel_dir)] + all_wheels)
    run = env_dir / "bin" / "pole-position"
    subprocess.check_call([str(run), "race", "--agent", "null"], env={"FAST_TEST": "1", "SDL_VIDEODRIVER": "dummy"})
