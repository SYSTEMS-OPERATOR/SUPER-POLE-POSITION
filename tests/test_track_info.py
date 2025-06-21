#!/usr/bin/env python3
"""Test suite for track_info module."""

import pytest  # noqa: F401

from super_pole_position.physics.track_info import load_track_info


def test_load_track_info():
    info = load_track_info("fuji_namco")
    assert info.length_meters > 0
    assert len(info.segments) == len(info.curvature)
