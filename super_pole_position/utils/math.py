"""Utility math functions for SUPER-POLE-POSITION."""

from __future__ import annotations


def factorial(n: int) -> int:
    """Return the factorial of ``n`` using an iterative algorithm."""

    if n < 0:
        raise ValueError("n must be non-negative")
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result
