#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 MIND INTERFACES, INC. All rights reserved.
# Licensed under the MIT License.

"""
conftest.py
Description: Test suite for conftest.
"""

import sys
from pathlib import Path

import pytest  # noqa: F401

# Ensure project root is on ``sys.path`` so the local gymnasium module is found
sys.path.append(str(Path(__file__).resolve().parents[1]))

# Skip the entire suite if gymnasium is unavailable
pytest.importorskip("gymnasium")

import os
import types
try:
    import pygame  # type: ignore
except Exception:  # pragma: no cover - optional
    pygame = types.SimpleNamespace(
        display=types.SimpleNamespace(init=lambda *a, **k: None),
        mixer=types.SimpleNamespace(),
        sndarray=types.SimpleNamespace(),
    )

os.environ.setdefault("FAST_TEST", "1")
os.environ["ALLOW_NET"] = "0"
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")


class _DummyChannel:
    def stop(self):
        pass

    def set_volume(self, *args, **kwargs):
        pass


class _DummySound:
    def __init__(self, *args, **kwargs):
        pass

    def set_volume(self, *args, **kwargs):
        pass

    def play(self, *args, **kwargs):
        return _DummyChannel()

pygame.mixer.init = lambda *a, **k: None
pygame.mixer.get_init = lambda: True
pygame.mixer.Sound = lambda *a, **k: _DummySound()
pygame.mixer.music = types.SimpleNamespace(set_volume=lambda *a, **k: None)
pygame.sndarray.make_sound = lambda *a, **k: _DummySound()

pygame.display.init = lambda *args, **kwargs: None

try:
    from super_pole_position.ui.arcade import ArcadeRenderer
    ArcadeRenderer.draw = lambda self, env: None
except Exception:
    pass


def pytest_configure(config):
    """Register custom markers when optional plugins are missing."""
    if not config.pluginmanager.hasplugin("timeout"):
        config.addinivalue_line(
            "markers",
            "timeout(timeout): no-op marker, pytest-timeout not installed",
        )
