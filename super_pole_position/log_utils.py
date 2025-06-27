from __future__ import annotations

import logging
from pathlib import Path


def init_playtest_logger() -> None:
    """Initialise root logger to file and stdout."""

    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "session.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s: %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(),
        ],
    )
