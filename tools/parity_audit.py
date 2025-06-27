#!/usr/bin/env python3
"""Minimal parity audit script."""

from __future__ import annotations

import argparse
import json
import hashlib
import sys
import numpy as np
from pathlib import Path
from typing import Any, Dict, List

sys.path.append(str(Path(__file__).resolve().parents[1]))
import super_pole_position as spp


def parse_args() -> argparse.Namespace:
    """Return CLI arguments."""

    parser = argparse.ArgumentParser(description="Run parity audit")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--laps", type=int, default=1)
    parser.add_argument("--frames", type=int, default=200)
    parser.add_argument("--audio", type=int, default=0)
    parser.add_argument("--dump", type=Path, required=True)
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--strict", action="store_true")
    return parser.parse_args()


def run_env(seed: int, frames: int, audio_frames: int) -> Dict[str, Any]:
    """Execute an episode and capture deterministic hashes."""

    env = spp.PolePositionEnv(render_mode="human")
    obs, _ = env.reset(seed=seed)
    rng = np.random.default_rng(seed)
    frame_hashes: List[int] = []
    audio_hashes: List[int] = []
    info: Dict[str, Any] = {}
    for i in range(frames):
        action = {
            "throttle": float(rng.random()),
            "brake": float(rng.random()),
            "steer": float(rng.uniform(-1.0, 1.0)),
        }
        obs, _, done, _, info = env.step(action)
        frame_hash = int(hashlib.md5(obs.tobytes()).hexdigest(), 16) & 0xFFFFFFFF
        frame_hashes.append(frame_hash)
        if i < audio_frames:
            audio_bytes = str(info.get("audio_frame", "")).encode()
            audio_hash = int(hashlib.md5(audio_bytes).hexdigest(), 16) & 0xFFFFFFFF
            audio_hashes.append(audio_hash)
        if done:
            break
    lap_time = getattr(env, "last_lap_time", None)
    if lap_time is None:
        lap_time = getattr(env, "lap_timer", 0.0)
    env.close()
    return {
        "lap_time": float(lap_time),
        "frame_hashes": frame_hashes,
        "audio_hashes": audio_hashes,
    }


def load_baseline(path: Path) -> Dict[str, Any] | None:
    """Load baseline JSON if available."""

    if path and path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            return None
    return None


def compute_metrics(run: Dict[str, Any], baseline: Dict[str, Any]) -> Dict[str, float]:
    """Return basic delta metrics between ``run`` and ``baseline``."""

    physics_delta = abs(run["lap_time"] - baseline.get("lap_time", 0.0))
    frames = run["frame_hashes"]
    base_frames = baseline.get("frame_hashes", [])
    mismatch = sum(1 for a, b in zip(frames, base_frames) if a != b)
    render_similarity = 1.0 - mismatch / max(len(frames), 1)
    audio = run["audio_hashes"]
    base_audio = baseline.get("audio_hashes", [])
    audio_mismatch = sum(1 for a, b in zip(audio, base_audio) if a != b)
    audio_similarity = 1.0 - audio_mismatch / max(len(audio), 1)
    return {
        "physics_delta": physics_delta,
        "render_similarity": render_similarity,
        "audio_similarity": audio_similarity,
    }


def main() -> None:
    """Entry point for parity audit."""

    args = parse_args()
    run = run_env(args.seed, args.frames, args.audio)
    baseline = load_baseline(args.baseline) if args.baseline else None
    if baseline is None:
        if args.baseline:
            args.baseline.write_text(json.dumps(run, indent=2))
            print(f"Created baseline at {args.baseline}")
        baseline = run
        metrics = {"physics_delta": 0.0, "render_similarity": 1.0, "audio_similarity": 1.0}
    else:
        metrics = compute_metrics(run, baseline)
    args.dump.write_text(json.dumps(metrics, indent=2))
    # TODO: use real SSIM instead of hash proxy
    # TODO: compare mel-spectrograms for audio
    # TODO: OCR HUD for lap time/score diffs
    log = (
        f"Physics Δ: {metrics['physics_delta']:.2f}s\n"
        f"Render similarity: {metrics['render_similarity']:.2f}\n"
        f"Audio similarity: {metrics['audio_similarity']:.2f}"
    )
    print(log, flush=True)
    threshold_fail = (
        metrics["physics_delta"] > 0.5 or metrics["render_similarity"] < 0.9 or metrics["audio_similarity"] < 0.9
    )
    if args.strict and threshold_fail:
        sys.exit(1)


if __name__ == "__main__":  # pragma: no cover - CLI
    main()
