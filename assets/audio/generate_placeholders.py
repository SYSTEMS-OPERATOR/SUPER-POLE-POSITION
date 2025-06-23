from __future__ import annotations

import math
from pathlib import Path
from typing import Callable
import wave

import numpy as np

SAMPLE_RATE = 32000


def write_wav(path: Path, data: np.ndarray) -> None:
    """Write mono 16-bit PCM WAV to ``path``."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes((data * 32767).astype(np.int16).tobytes())


def engine_loop(duration: float = 1.0) -> np.ndarray:
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    base = 0.4 * np.sin(2 * math.pi * 220 * t)
    harm = 0.2 * np.sin(2 * math.pi * 440 * t)
    return base + harm


def skid(duration: float = 0.3) -> np.ndarray:
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    noise = np.random.uniform(-1.0, 1.0, len(t))
    fade = np.exp(-10 * t)
    return noise * fade * 0.5


def crash(duration: float = 0.8) -> np.ndarray:
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    noise = np.random.uniform(-1.0, 1.0, len(t))
    fade = np.exp(-6 * t)
    return noise * fade


def checkpoint(duration: float = 0.2) -> np.ndarray:
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    tone = np.sin(2 * math.pi * 880 * t)
    envelope = np.exp(-8 * t)
    return tone * envelope



def menu_tick(duration: float = 0.1) -> np.ndarray:
    """Return short beep for menu navigation."""

    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    tone = np.sin(2 * math.pi * 660 * t)
    envelope = np.exp(-12 * t)
    return tone * envelope

  
def _square_wave(freq: float, duration: float) -> np.ndarray:
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    return 0.5 * np.sign(np.sin(2 * math.pi * freq * t))


def prepare_voice() -> np.ndarray:
    notes = [(440, 0.15), (660, 0.15), (880, 0.3)]
    return np.concatenate([_square_wave(f, d) for f, d in notes])


def final_lap_voice() -> np.ndarray:
    notes = [(660, 0.2), (660, 0.2), (880, 0.3)]
    return np.concatenate([_square_wave(f, d) for f, d in notes])


def goal_voice() -> np.ndarray:
    notes = [(523, 0.2), (659, 0.25), (784, 0.35)]
    return np.concatenate([_square_wave(f, d) for f, d in notes])


def bgm_theme() -> np.ndarray:
    melody = [(440, 0.2), (554, 0.2), (659, 0.4), (587, 0.2), (659, 0.2)]
    return np.concatenate([_square_wave(f, d) for f, d in melody])


GENERATORS: dict[str, Callable[[], np.ndarray]] = {
    "engine_loop.wav": engine_loop,
    "skid.wav": skid,
    "crash.wav": crash,
    "checkpoint.wav": checkpoint,
    "menu_tick.wav": menu_tick,
    "prepare.wav": prepare_voice,
    "final_lap.wav": final_lap_voice,
    "goal.wav": goal_voice,
    "bgm.wav": bgm_theme,
}


def generate_all(base: Path | None = None) -> None:
    """Generate simple placeholder WAV files."""
    base = base or Path(__file__).resolve().parent
    for name, func in GENERATORS.items():
        out = base / name
        if out.exists() and out.stat().st_size > 0:
            continue
        data = func()
        write_wav(out, data)


if __name__ == "__main__":
    generate_all()
