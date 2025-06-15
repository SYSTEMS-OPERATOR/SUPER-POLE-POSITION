#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 MIND INTERFACES, INC. All rights reserved.
# Licensed under the MIT License.

"""
test_ascii_sprites.py
Description: Test suite for test_ascii_sprites.
"""

import pytest  # noqa: F401
pygame = pytest.importorskip("pygame")

from super_pole_position.ui.sprites import ascii_surface, CAR_ART  # noqa: E402


def test_ascii_surface():
    pygame.display.init()
    surf = ascii_surface(CAR_ART)
    assert surf is not None
    assert surf.get_width() == len(CAR_ART[0])
    pygame.display.quit()
