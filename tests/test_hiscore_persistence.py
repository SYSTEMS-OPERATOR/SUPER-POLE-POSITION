#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 MIND INTERFACES, INC. All rights reserved.
# Licensed under the MIT License.

"""
test_hiscore_persistence.py
Description: Test suite for test_hiscore_persistence.
"""

import pytest  # noqa: F401

from pathlib import Path
from super_pole_position.evaluation.scores import load_scores, update_scores, reset_scores


def test_hiscore_persistence(tmp_path: Path) -> None:
    file = tmp_path / "scores.json"
    reset_scores(file)
    update_scores(file, "A", 100)
    update_scores(file, "B", 50)
    scores = load_scores(file)
    assert scores[0]["score"] == 100
    update_scores(file, "C", 150)
    scores2 = load_scores(file)
    assert scores2[0]["score"] == 150 and len(scores2) == 3
