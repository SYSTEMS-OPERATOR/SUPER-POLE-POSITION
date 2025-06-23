"""Minimal HTTP API for scoreboards."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from ..evaluation import scores, lap_times

try:  # pragma: no cover - optional dependency
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel
except Exception:  # pragma: no cover - fastapi missing
    FastAPI = None
    BaseModel = object  # type: ignore
    HTTPException = Exception
    JSONResponse = dict  # type: ignore


class ScoreIn(BaseModel):
    """Score entry model."""

    name: str
    score: int


class LapIn(BaseModel):
    """Lap time entry model."""

    name: str
    lap_ms: int


SCORES_FILE = Path(os.getenv("SPP_SCORES", scores._DEFAULT_FILE))
LAPS_FILE = Path(os.getenv("SPP_LAPS", lap_times._DEFAULT_FILE))


def build_app() -> "FastAPI":
    """Return a FastAPI app serving the scoreboard."""

    if FastAPI is None:
        raise RuntimeError("fastapi not available")

    app = FastAPI(title="SPP Scoreboard")

    @app.get("/scores")
    def get_scores() -> Any:
        return {"scores": scores.load_scores(SCORES_FILE)}

    @app.get("/laps")
    def get_laps() -> Any:
        return {"laps": lap_times.load_lap_times(LAPS_FILE)}

    from fastapi import Body

    @app.post("/scores")
    def post_score(entry: ScoreIn = Body(...)) -> Any:
        try:
            scores.update_scores(SCORES_FILE, entry.name, entry.score)
        except Exception as exc:  # pragma: no cover - file error
            raise HTTPException(status_code=500, detail=str(exc))
        return JSONResponse({"ok": True})

    @app.post("/laps")
    def post_lap(entry: LapIn = Body(...)) -> Any:
        try:
            lap_times.update_lap_times(LAPS_FILE, entry.name, entry.lap_ms)
        except Exception as exc:  # pragma: no cover - file error
            raise HTTPException(status_code=500, detail=str(exc))
        return JSONResponse({"ok": True})

    return app


def start(host: str = "127.0.0.1", port: int = 8000) -> None:
    """Start the API server if FastAPI is available."""

    if FastAPI is None:
        print("FastAPI not installed", flush=True)
        return
    import uvicorn  # pragma: no cover - runtime import

    uvicorn.run(build_app(), host=host, port=port)
