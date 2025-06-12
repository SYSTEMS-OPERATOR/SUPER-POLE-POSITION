"""Utility for writing simple JSON/CSV benchmark logs."""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from .metrics import summary

# Root directory for benchmark files (can be patched in tests)
BENCH_ROOT = Path("benchmarks")


def log_episode(env, file: Path | None = None, step_file: Path | None = None) -> Path:
    """Write a JSON summary and step CSV for ``env``.

    :param env: Environment with metrics attributes.
    :param file: Optional explicit path for the summary JSON. Defaults to
        ``benchmarks/YYYY-MM-DD/<timestamp>.json``.
    :param step_file: Optional explicit path for per-step CSV. Defaults to
        ``benchmarks/YYYY-MM-DD/<timestamp>-steps.csv``.
    :return: Path to the file written.
    """
    date_dir = BENCH_ROOT / datetime.now(timezone.utc).strftime("%Y-%m-%d")
    date_dir.mkdir(parents=True, exist_ok=True)
    if file is None:
        timestamp = datetime.now(timezone.utc).strftime("%H%M%S")
        file = date_dir / f"{timestamp}.json"
    if step_file is None:
        step_file = date_dir / f"{file.stem}-steps.csv"

    data = summary(env)
    data["timestamp"] = datetime.now(timezone.utc).isoformat()
    file.write_text(json.dumps(data, indent=2))

    # Per-step CSV log if env provides ``step_log``
    if getattr(env, "step_log", None):
        fields = list(env.step_log[0].keys()) if env.step_log else []
        with step_file.open("w", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=fields)
            writer.writeheader()
            for row in env.step_log:
                writer.writerow(row)

    return file
