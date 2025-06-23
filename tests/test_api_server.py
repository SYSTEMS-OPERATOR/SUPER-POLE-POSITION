#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test scoreboard API."""

import os
import sys
from pathlib import Path

import importlib
import pytest

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))

skip_if_no_fastapi = pytest.mark.skipif(
    importlib.util.find_spec("fastapi") is None,
    reason="fastapi not installed",
)


@skip_if_no_fastapi
def test_scores_endpoints(tmp_path: Path) -> None:
    scores_path = tmp_path / "scores.json"
    laps_path = tmp_path / "laps.json"
    os.environ["SPP_SCORES"] = str(scores_path)
    os.environ["SPP_LAPS"] = str(laps_path)
    from super_pole_position.server import api
    import importlib
    importlib.reload(api)
    app = api.build_app()
    from fastapi.testclient import TestClient

    client = TestClient(app)
    resp = client.get("/scores")
    assert resp.status_code == 200
    assert resp.json() == {"scores": []}

    resp = client.get("/laps")
    assert resp.status_code == 200
    assert resp.json() == {"laps": []}

    resp = client.post("/scores", json={"name": "bot", "score": 5})
    assert resp.status_code == 200

    resp = client.post("/laps", json={"name": "bot", "lap_ms": 42000})
    assert resp.status_code == 200

    resp = client.get("/scores")
    data = resp.json()
    assert any(entry["name"] == "bot" for entry in data["scores"])

    resp = client.get("/laps")
    data = resp.json()
    assert any(entry["name"] == "bot" for entry in data["laps"])
