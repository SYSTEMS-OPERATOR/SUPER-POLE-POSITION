from __future__ import annotations

from typing import List


def summary(env) -> dict:
    """Extract metrics from env for leaderboard."""
    return {
        "reward": getattr(env, "episode_reward", 0.0),
        "qualifying_time": getattr(env, "qualifying_time", None),
        "passes": getattr(env, "passes", 0),
        "crashes": getattr(env, "crashes", 0),
        "gear_shifts": env.cars[0].shift_count if env.cars else 0,
    }


def lap_time(rewards: List[float]) -> float:
    """Compute pseudo lap time as inverse of total reward."""
    return 1.0 / max(sum(rewards), 1e-6)
