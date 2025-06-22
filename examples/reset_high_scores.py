#!/usr/bin/env python3
"""Utility to clear the local high-score table."""

from __future__ import annotations

import os
from pathlib import Path

from super_pole_position.evaluation.scores import reset_scores


def main() -> None:
    """Reset the scoreboard file to an empty list."""
    default = Path(__file__).resolve().parents[1] / "super_pole_position" / "evaluation" / "scores.json"
    file = Path(os.getenv("SPP_SCORES", default))
    reset_scores(file)
    print(f"High score table reset at {file}")


if __name__ == "__main__":  # pragma: no cover - manual utility
    main()
