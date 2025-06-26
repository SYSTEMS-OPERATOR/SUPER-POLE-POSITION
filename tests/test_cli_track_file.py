import sys
import pytest  # noqa: F401
from super_pole_position import cli


def test_cli_track_file(monkeypatch, tmp_path):
    recorded = {}

    class DummyEnv:
        def __init__(self, *_, track_file=None, **__):  # type: ignore
            recorded['file'] = track_file
            self.score = 0

        def close(self):
            pass

    monkeypatch.setitem(sys.modules, "pygame", None)
    monkeypatch.setattr(cli, "safe_run_episode", lambda env, agents: None)
    monkeypatch.setattr(cli, "update_leaderboard", lambda *a, **k: None)
    monkeypatch.setattr(cli, "summary", lambda env: {})
    monkeypatch.setattr(cli, "update_scores", lambda *a, **k: None)
    monkeypatch.setattr(cli, "PolePositionEnv", DummyEnv)
    track = tmp_path / "track.json"
    track.write_text("{}")
    monkeypatch.setattr(sys, "argv", ["spp", "race", "--track-file", str(track)])
    monkeypatch.setenv("FAST_TEST", "1")

    cli.main()
    assert recorded.get("file") == str(track)
