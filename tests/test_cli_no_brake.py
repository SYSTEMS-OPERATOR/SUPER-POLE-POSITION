import os
import sys
import pytest  # noqa: F401
from super_pole_position import cli


def fake_run_episode(env, agents):
    return 0.0


def test_cli_no_brake(monkeypatch):
    monkeypatch.setitem(sys.modules, "pygame", None)
    monkeypatch.setattr(cli, "run_episode", fake_run_episode)
    monkeypatch.setattr(sys, "argv", ["spp", "race", "--no-brake"])
    monkeypatch.setenv("FAST_TEST", "1")
    cli.main()
    assert os.environ.get("DISABLE_BRAKE") == "1"
