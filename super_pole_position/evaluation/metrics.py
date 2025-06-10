from __future__ import annotations

from typing import List


def lap_time(rewards: List[float]) -> float:
    """Compute pseudo lap time as inverse of total reward."""
    return 1.0 / max(sum(rewards), 1e-6)
