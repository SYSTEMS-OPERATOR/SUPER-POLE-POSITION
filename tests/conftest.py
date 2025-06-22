#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 MIND INTERFACES, INC. All rights reserved.
# Licensed under the MIT License.

"""
conftest.py
Description: Test suite for conftest.
"""

import pytest  # noqa: F401

# Skip the entire suite if gymnasium is unavailable
pytest.importorskip("gymnasium")

import os
import sys
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
