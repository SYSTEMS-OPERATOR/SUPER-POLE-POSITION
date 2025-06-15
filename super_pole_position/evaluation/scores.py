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
    file.write_text(json.dumps({"scores": scores}, indent=2))


def reset_scores(file: Path | None = None) -> None:
    """Clear all scores in ``file``."""

    file = file or _DEFAULT_FILE
    file.write_text(json.dumps({"scores": []}, indent=2))
