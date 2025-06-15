#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 MIND INTERFACES, INC. All rights reserved.
# Licensed under the MIT License.

"""
test_cli_render_skip.py
Description: Test suite for test_cli_render_skip.
"""

import sys
import pytest  # noqa: F401
from super_pole_position import cli


def test_cli_render_skip(monkeypatch):
    monkeypatch.setitem(sys.modules, "pygame", None)
    monkeypatch.setattr(sys, "argv", ["spp", "race", "--render"])
    with pytest.raises(SystemExit) as exc:
        cli.main()
    assert exc.value.code == 1
