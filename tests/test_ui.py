#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 MIND INTERFACES, INC. All rights reserved.
# Licensed under the MIT License.

"""
test_ui.py
Description: Test suite for test_ui.
"""


import pytest  # noqa: F401
ui = pytest.importorskip('super_pole_position.ui.arcade')

def test_available():
    assert isinstance(ui.available(), bool)
