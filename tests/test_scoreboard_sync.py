#!/usr/bin/env python3
"""Test scoreboard sync service."""

from pathlib import Path

from super_pole_position.server import sync


def test_sync_once(monkeypatch, tmp_path: Path) -> None:
    file = tmp_path / "scores.json"

    class Dummy:
        status = 200

        def read(self) -> bytes:
            return b'{"scores": [{"name": "remote", "score": 5}]}'

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

    def fake_urlopen(url: str, timeout: int = 1):
        return Dummy()

    monkeypatch.setattr(sync.request, "urlopen", fake_urlopen)

    assert sync.sync_once(file, host="dummy", port=0)
    assert "remote" in file.read_text()
