from datetime import datetime, timezone
from pathlib import Path

from super_pole_position.envs.pole_position import PolePositionEnv
from super_pole_position.evaluation import logger as bench_logger


def test_log_episode_creates_files(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    bench_logger.BENCH_ROOT = Path("benchmarks")

    env = PolePositionEnv(render_mode="human")
    env.reset()
    env.remaining_time = 0  # force done
    env.step((0, 0, 0.0))
    env.close()

    date_dir = tmp_path / "benchmarks" / datetime.now(timezone.utc).strftime("%Y-%m-%d")
    files = list(date_dir.iterdir())
    assert any(f.suffix == ".json" for f in files)
    assert any(f.suffix == ".csv" for f in files)
