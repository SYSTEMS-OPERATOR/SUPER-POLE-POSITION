import sys
import pytest  # noqa: F401
from super_pole_position import cli


def test_cli_invokes_outro(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = []

    class DummyEnv:
        def __init__(self, *_, **__):
            self.score = 123
            self.screen = None

        def close(self) -> None:
            pass

    monkeypatch.setitem(sys.modules, "pygame", None)
    monkeypatch.setattr(cli, "safe_run_episode", lambda env, agents: None)
    monkeypatch.setattr(cli, "update_leaderboard", lambda *a, **k: None)
    monkeypatch.setattr(cli, "summary", lambda env: {})
    monkeypatch.setattr(cli, "update_scores", lambda *a, **k: None)
    monkeypatch.setattr(cli, "PolePositionEnv", DummyEnv)

    def fake_show(screen, score, duration=5.0):
        calls.append(score)

    monkeypatch.setattr(cli, "show_race_outro", fake_show)
    monkeypatch.setattr(sys, "argv", ["spp", "race"])
    monkeypatch.setenv("FAST_TEST", "1")

    cli.main()

    assert calls == [123]

