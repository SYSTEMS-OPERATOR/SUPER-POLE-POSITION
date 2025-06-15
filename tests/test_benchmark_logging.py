import json
from datetime import datetime, timezone
import pytest  # noqa: F401

from super_pole_position.matchmaking import arena
from super_pole_position.envs.pole_position import PolePositionEnv
from super_pole_position.agents.base_llm_agent import NullAgent


def test_benchmark_logging(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    env = PolePositionEnv(render_mode="human")
    env.reset()
    agents = (NullAgent(), NullAgent())
    arena.run_episode(env, agents)
    date_dir = tmp_path / "benchmarks" / datetime.now(timezone.utc).strftime("%Y-%m-%d")
    files = list(date_dir.glob("*.json"))
    assert files
    data = json.loads(files[0].read_text())
    assert {"agent", "track", "result", "perf"} <= data.keys()
