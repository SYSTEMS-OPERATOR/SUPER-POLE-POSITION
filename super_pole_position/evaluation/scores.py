#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 MIND INTERFACES, INC. All rights reserved.
# Licensed under the MIT License.

"""
scores.py
Description: Module for Super Pole Position.
"""


from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict
from urllib import request
import os


_DEFAULT_FILE = Path(__file__).resolve().parent / "scores.json"


def load_scores(file: Path | None = None) -> List[Dict]:
    """Return list of score dicts from ``file``."""

    file = file or _DEFAULT_FILE
    if file.exists():
        try:
            data = json.loads(file.read_text())
            return data.get("scores", [])
        except Exception:
            return []
    return []


def update_scores(file: Path | None, name: str, score: int) -> None:
    """Record ``score`` for ``name`` in ``file``."""

    file = file or _DEFAULT_FILE
    scores = load_scores(file)
    scores.append({"name": name, "score": int(score)})
    scores = sorted(scores, key=lambda s: -s["score"])[:10]
    try:
        file.write_text(json.dumps({"scores": scores}, indent=2))
    except Exception as exc:  # pragma: no cover - file error
        print(f"update_scores error: {exc}", flush=True)


def reset_scores(file: Path | None = None) -> None:
    """Clear all scores in ``file``."""

    file = file or _DEFAULT_FILE
    try:
        file.write_text(json.dumps({"scores": []}, indent=2))
    except Exception as exc:  # pragma: no cover - file error
        print(f"reset_scores error: {exc}", flush=True)


def submit_score_http(
    name: str, score: int, host: str = "127.0.0.1", port: int = 8000
) -> bool:
    """POST ``score`` for ``name`` to the scoreboard server.

    Returns ``True`` on success.
    """

    if os.getenv("ALLOW_NET") != "1":
        return False
    url = f"http://{host}:{port}/scores"
    data = json.dumps({"name": name, "score": int(score)}).encode()
    req = request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with request.urlopen(req, timeout=1) as resp:  # pragma: no cover - network
            return 200 <= resp.status < 300
    except Exception:
        return False
