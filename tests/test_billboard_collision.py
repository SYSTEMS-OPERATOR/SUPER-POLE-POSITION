#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_billboard_collision.py
Description: Test billboard collision time penalty.
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from super_pole_position.envs.pole_position import PolePositionEnv
from super_pole_position.physics.track import Track, Obstacle


def test_billboard_collision_time_bleed():
    track = Track(width=100, height=100, obstacles=[Obstacle(x=50, y=50, width=4, height=4, billboard=True)])
    env = PolePositionEnv(render_mode="human", mode="race")
    env.reset()
    env.track = track
    env.cars[0].x = 50
    env.cars[0].y = 50
    env.start_timer = 0
    before = env.remaining_time
    env.step((True, False, 0.0))
    assert env.remaining_time < before
    assert env.crash_timer > 0
    assert not env.track.obstacles
    env.close()
