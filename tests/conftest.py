#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 MIND INTERFACES, INC. All rights reserved.
# Licensed under the MIT License.

"""
conftest.py
Description: Test suite for conftest.
"""

import pytest  # noqa: F401
import os
import sys
import types
try:
    import pygame  # type: ignore
except Exception:  # pragma: no cover - optional
    pygame = types.SimpleNamespace(display=types.SimpleNamespace(init=lambda *a, **k: None))

os.environ.setdefault("FAST_TEST", "1")
os.environ["ALLOW_NET"] = "0"
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

class _DummyWave:
    bytes_per_sample = 2
    num_channels = 2
    sample_rate = 44100
    audio_data = b""

    @staticmethod
    def from_wave_file(*args, **kwargs):
        return _DummyWave()

    def play(self, *args, **kwargs):
        return None

def _play_buffer(*args, **kwargs):
    class _Dummy:
        def stop(self):
            pass
    return _Dummy()

sys.modules["simpleaudio"] = types.SimpleNamespace(
    WaveObject=_DummyWave,
    play_buffer=_play_buffer,
)

pygame.display.init = lambda *args, **kwargs: None

try:
    from super_pole_position.ui.arcade import ArcadeRenderer
    ArcadeRenderer.draw = lambda self, env: None
except Exception:
    pass
