import sys
import pytest  # noqa: F401
from super_pole_position import cli


def test_cli_difficulty_option(monkeypatch: pytest.MonkeyPatch) -> None:
    recorded = {}

    class DummyEnv:
        def __init__(self, *_, difficulty: str = "beginner", **__):
            recorded["difficulty"] = difficulty
            self.score = 0

        def close(self) -> None:
            pass

    monkeypatch.setitem(sys.modules, "pygame", None)
    monkeypatch.setattr(cli, "safe_run_episode", lambda env, agents: None)
    monkeypatch.setattr(cli, "update_leaderboard", lambda *a, **k: None)
    monkeypatch.setattr(cli, "summary", lambda env: {})
    monkeypatch.setattr(cli, "update_scores", lambda *a, **k: None)
    monkeypatch.setattr(cli, "PolePositionEnv", DummyEnv)
    monkeypatch.setattr(sys, "argv", ["spp", "race", "--difficulty", "expert"])
    monkeypatch.setenv("FAST_TEST", "1")

    cli.main()
    assert recorded.get("difficulty") == "expert"
