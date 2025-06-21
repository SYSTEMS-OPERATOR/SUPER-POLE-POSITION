#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 MIND INTERFACES, INC. All rights reserved.
# Licensed under the MIT License.

"""
test_hud_render.py
Description: Test suite for test_hud_render.
"""

import pytest  # noqa: F401

import pygame
pygame = pytest.importorskip("pygame")  # noqa: E402

from super_pole_position.envs.pole_position import PolePositionEnv  # noqa: E402
from super_pole_position.ui.arcade import Pseudo3DRenderer  # noqa: E402


def test_hud_render_smoke():
    pygame.display.init()
    screen = pygame.display.set_mode((320, 240))
    env = PolePositionEnv(render_mode="human")
    env.reset()
    renderer = Pseudo3DRenderer(screen)
    renderer.draw(env)
    pygame.display.quit()
