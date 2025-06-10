"""Minimal pygame viewer used during local races."""

try:
    import pygame  # type: ignore
except Exception:  # pragma: no cover
    pygame = None


def available() -> bool:
    return pygame is not None
