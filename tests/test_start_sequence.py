#!/usr/bin/env python3
"""Test rendering of the READY/SET/GO text."""

import pytest

import pygame
pygame = pytest.importorskip("pygame")  # noqa: E402

from super_pole_position.envs.pole_position import PolePositionEnv  # noqa: E402
from super_pole_position.ui.arcade import Pseudo3DRenderer  # noqa: E402


def test_start_sequence_draw() -> None:
    pygame.display.init()
    screen = pygame.display.set_mode((320, 240))
    env = PolePositionEnv(render_mode="human")
    env.reset()
    env.start_phase = "READY"
    renderer = Pseudo3DRenderer(screen)
    renderer.draw(env)
    pygame.display.quit()
