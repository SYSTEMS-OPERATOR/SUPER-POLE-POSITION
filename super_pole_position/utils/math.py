"""Utility math functions for SUPER-POLE-POSITION."""

from __future__ import annotations


def factorial(n: int) -> int:
    """Return the factorial of ``n`` using a recursive algorithm."""
    if n < 0:
        raise ValueError("n must be non-negative")
    if n in (0, 1):
        return 1
    return n * factorial(n - 1)
