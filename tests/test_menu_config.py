#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 MIND INTERFACES, INC. All rights reserved.
# Licensed under the MIT License.

"""
test_menu_config.py
Description: Test suite for test_menu_config.
"""

import pytest  # noqa: F401

from super_pole_position.ui.menu import MenuState


def test_menu_navigation_and_config():
    state = MenuState()
    # set difficulty to expert
    state.handle('RIGHT')
    # move to audio and turn off
    state.handle('DOWN')
    state.handle('RIGHT')
    # move to track and choose seaside
    state.handle('DOWN')
    state.handle('RIGHT')
    # confirm
    cfg = state.handle('ENTER')
    assert cfg['difficulty'] == 'expert'
    assert cfg['audio'] is False
    assert cfg['track'] == 'seaside'


def test_menu_escape_returns_none():
    state = MenuState()
    assert state.handle('ESC') is None
