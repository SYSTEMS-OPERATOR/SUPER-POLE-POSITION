#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 MIND INTERFACES, INC. All rights reserved.
# Licensed under the MIT License.

"""
test_cli_headless.py
Description: Test suite for test_cli_headless.
"""

import os
import subprocess
import sys
import pytest


@pytest.mark.skipif(not os.getenv("CI_SLOW_TESTS"), reason="slow test")
def test_cli_headless() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "super_pole_position.cli", "race"],
        env={**os.environ, "FAST_TEST": "1"},
        timeout=5,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert result.returncode == 0
