#!/usr/bin/env python3
"""Ensure CLI forwards --player to env and scoreboard."""

import sys
from pathlib import Path

import pytest  # noqa: F401

from super_pole_position import cli


def test_cli_player_name(monkeypatch: pytest.MonkeyPatch) -> None:
    recorded = {}

    class DummyEnv:
        def __init__(self, *_, player_name: str = "", **__):  # type: ignore
            recorded["name"] = player_name
            self.score = 0

        def close(self) -> None:
            pass

    monkeypatch.setitem(sys.modules, "pygame", None)
    monkeypatch.setattr(cli, "run_episode", lambda env, agents: None)
    monkeypatch.setattr(cli, "update_leaderboard", lambda *a, **k: None)
    monkeypatch.setattr(cli, "summary", lambda env: {})
    names: list[str] = []

    def fake_update_scores(file: Path, name: str, score: int) -> None:
        names.append(name)

    monkeypatch.setattr(cli, "update_scores", fake_update_scores)
    monkeypatch.setattr(cli, "PolePositionEnv", DummyEnv)
    monkeypatch.setattr(sys, "argv", ["spp", "race", "--player", "AAA"])
    monkeypatch.setenv("FAST_TEST", "1")

    cli.main()
    assert recorded.get("name") == "AAA"
    assert names == ["AAA"]
