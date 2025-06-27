#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for math utility functions."""

import importlib.util
import os
import pathlib
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest  # noqa: F401

MODULE_PATH = pathlib.Path(__file__).resolve().parents[1] / "super_pole_position" / "utils" / "math.py"
spec = importlib.util.spec_from_file_location("sp_math", MODULE_PATH)
sp_math = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sp_math)  # type: ignore
factorial = sp_math.factorial


def test_factorial_base_cases():
    assert factorial(0) == 1
    assert factorial(1) == 1


def test_factorial_positive():
    assert factorial(5) == 120


def test_factorial_negative():
    with pytest.raises(ValueError):
        factorial(-1)


def test_factorial_type_error():
    with pytest.raises(TypeError):
        factorial(3.5)


def test_factorial_large():
    import math
    assert factorial(100) == math.factorial(100)
