import os
import sys
import pytest  # noqa: F401
from super_pole_position import cli


def fake_run_episode(env: object, agents: object) -> float:
    return 0.0


def test_cli_mute_bgm(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(sys.modules, "pygame", None)
    monkeypatch.setattr(cli, "run_episode", fake_run_episode)
    monkeypatch.setattr(sys, "argv", ["spp", "qualify", "--mute-bgm"])
    monkeypatch.setenv("FAST_TEST", "1")
    cli.main()
    assert os.environ.get("MUTE_BGM") == "1"
