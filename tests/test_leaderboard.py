#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 MIND INTERFACES, INC. All rights reserved.
# Licensed under the MIT License.

"""
test_leaderboard.py
Description: Test suite for test_leaderboard.
"""

import pytest  # noqa: F401

import json
from pathlib import Path

from super_pole_position.matchmaking.arena import update_leaderboard


def test_update_leaderboard(tmp_path: Path) -> None:
    file = tmp_path / "lb.json"
    update_leaderboard(file, "agent", {"reward": 1.0})
    data = json.loads(file.read_text())
    assert data["results"][0]["name"] == "agent"
