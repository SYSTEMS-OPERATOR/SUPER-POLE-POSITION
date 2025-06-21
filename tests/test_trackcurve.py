#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for TrackCurve helper."""

import math
import pytest

from super_pole_position.physics.track_curve import TrackCurve
from super_pole_position.physics.car import Car
from super_pole_position.physics.track import Track


def test_straight_curve():
    curve = TrackCurve.from_tuples([(0.0, 0.0, 0.0, 10.0)])
    assert curve.total_length == pytest.approx(10.0)
    assert curve.point_at(5.0) == pytest.approx((5.0, 0.0))
    tx, ty = curve.tangent_at(5.0)
    nx, ny = curve.normal_at(5.0)
    assert (tx, ty) == pytest.approx((1.0, 0.0))
    assert (nx, ny) == pytest.approx((0.0, 1.0))


def test_curve_in_track_on_road():
    curve = TrackCurve.from_tuples([(0.0, 0.0, 0.0, 10.0)])
    track = Track(width=10.0, height=2.0, road_width=2.0, curve=curve)
    car = Car(x=5.0, y=1.0)
    assert track.on_road(car)
    car.y = 2.1
    assert not track.on_road(car)
