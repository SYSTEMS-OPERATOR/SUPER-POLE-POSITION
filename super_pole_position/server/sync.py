from __future__ import annotations

"""Background scoreboard sync service."""

import json
import os
import time
from pathlib import Path
from urllib import request

from ..evaluation import scores


DEFAULT_INTERVAL = 60.0


def sync_once(file: Path, host: str = "127.0.0.1", port: int = 8000) -> bool:
    """Fetch remote scores and merge with local scoreboard."""
    url = f"http://{host}:{port}/scores"
    try:
        with request.urlopen(url, timeout=1) as resp:  # pragma: no cover - network
            data = json.loads(resp.read())
            remote = data.get("scores", [])
    except Exception as exc:  # pragma: no cover - network failure
        print(f"sync fetch error: {exc}", flush=True)
        return False

    local = scores.load_scores(file)
    merged = sorted(local + remote, key=lambda s: -s["score"])[:10]
    try:
        file.write_text(json.dumps({"scores": merged}, indent=2))
    except Exception as exc:  # pragma: no cover - file error
        print(f"sync write error: {exc}", flush=True)
        return False
    return True


def start_service(
    host: str = "127.0.0.1",
    port: int = 8000,
    interval: float = DEFAULT_INTERVAL,
) -> None:
    """Run sync loop. Stops after one iteration in FAST_TEST mode."""
    file = Path(os.getenv("SPP_SCORES", scores._DEFAULT_FILE))
    once = os.getenv("FAST_TEST", "") == "1"
    while True:
        sync_once(file, host, port)
        if once:
            break
        time.sleep(interval)
