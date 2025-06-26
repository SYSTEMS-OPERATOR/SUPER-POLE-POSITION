#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 MIND INTERFACES, INC. All rights reserved.
# Licensed under the MIT License.


"""
pole_position.py
Description: Module for Super Pole Position.
"""

import os

# Hide pygame's greeting for cleaner logs
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
import numpy as np
import gymnasium as gym
import time
from pathlib import Path
import importlib.util

try:
    import pygame  # optional dependency for graphics
    from pygame import mixer as pg_mixer  # audio via pygame
except Exception:  # pragma: no cover - optional dependency may be missing
    pygame = None
    pg_mixer = None

from ..physics.car import Car
from ..physics.track import Track
from ..physics.traffic_car import TrafficCar
import random
from random import Random
from ..ai_cpu import CPUCar
from ..agents.controllers import GPTPlanner, LowLevelController, LearningAgent
from ..ui.arcade import Pseudo3DRenderer

from ..config import load_parity_config
from ..config import load_arcade_parity
from ..evaluation import submit_score_http, submit_lap_time_http

_PARITY_CONFIG = load_arcade_parity()
ENGINE_BASE_FREQ = _PARITY_CONFIG.get("engine_base_freq", 400.0)
ENGINE_PITCH_FACTOR = _PARITY_CONFIG.get("engine_pitch_factor", 3000.0)


def engine_pitch(rpm: float, gear: int = 0) -> float:
    """Return engine frequency in Hz for ``rpm`` and ``gear``."""

    gear_factor = 1.0 + 0.1 * max(0, gear)
    return ENGINE_BASE_FREQ + ENGINE_PITCH_FACTOR * rpm * gear_factor

FAST_TEST = bool(int(os.getenv("FAST_TEST", "0")))
PARITY_CFG = load_parity_config()


def _seed_all(seed: int) -> None:
    """Seed all random generators used by the environment."""

    random.seed(seed)
    np.random.seed(seed)
    try:  # pragma: no cover - optional dependency
        import torch  # type: ignore

        torch.manual_seed(seed)
    except Exception:
        pass


def ordinal(n: int) -> str:
    """Return ordinal string for an integer (1 -> 1ST)."""
    if 10 <= n % 100 <= 20:
        suffix = "TH"
    else:
        suffix = {1: "ST", 2: "ND", 3: "RD"}.get(n % 10, "TH")
    return f"{n}{suffix}"


def _qualifying_bonus(time_s: float) -> tuple[int, int]:
    """Return (rank, score bonus) for a qualifying time."""
    if time_s < 55.0:
        return 1, 5000
    if time_s < 58.0:
        return 3, 3000
    return 6, 1000

class PolePositionEnv(gym.Env):
    """
    A multi-car racing environment with:
    - Toroidal 2D track
    - Binaural audio based on each car's speed
    - GPT-based high-level plan for Car B
    - A single discrete action for Car A (player or random)
    - Optional hyper mode for uncapped speed
    """

    metadata = {"render_modes": ["human"], "render_fps": 60}

    def __init__(
        self,
        render_mode: str = "human",
        mode: str = "race",
        track_name: str | None = None,
        track_file: str | None = None,
        hyper: bool = False,
        player_name: str = "PLAYER",
        slipstream: bool = True,
        difficulty: str = "beginner",
        start_position: int | None = None,
        seed: int | None = None,
        mode_2600: bool = False,
    ) -> None:
        """Create a Pole Position environment.

        :param render_mode: ``human`` for pygame output.
        :param mode: ``race`` or ``qualify``.
        :param track_name: Optional built-in track to load.
        :param track_file: Path to a custom track JSON file.
        :param hyper: If ``True`` doubles gear limits for extreme speed.
        :param player_name: Name recorded in the high-score table.
        :param start_position: Optional grid position shown at race start.
        """

        super().__init__()
        _seed_all(seed)
        self.rng = Random(seed)
        self.np_rng = np.random.default_rng(seed)


        self.render_mode = render_mode
        self.mode = mode
        self.hyper = hyper
        self.player_name = player_name
        self.slipstream_enabled = slipstream
        self.difficulty = difficulty
        self.start_position = start_position
        self.mode_2600 = mode_2600
        self._start_pos_shown = False
        self.track_file = track_file

        limits = {
            "beginner": {"race": 90.0, "qualify": 73.0},
            "expert": {"race": 75.0, "qualify": 60.0},
        }
        self.time_limit = limits.get(difficulty, limits["beginner"])[self.mode]
        self.traffic_count = 7 if self.mode == "race" else 0
        if self.mode_2600:
            self.traffic_count = 0
        if FAST_TEST:
            self.time_limit = min(self.time_limit, 3.0)
            self.traffic_count = 1

        # Track & cars
        if track_file:
            self.track = Track.from_file(track_file)
        else:
            self.track = (
                Track.load(track_name) if track_name else Track(width=200.0, height=200.0)
            )
        self.cars = [Car(x=50, y=50), Car(x=150, y=150)]
        if self.hyper:
            for car in self.cars:
                car.gear_max = [g * 2 for g in car.gear_max]
                car.max_speed = car.gear_max[-1]
                # Remove speed clamp for Hyper mode
                car.unlimited = True
        if self.mode_2600:
            self._2600_offsets = [-2.0, 0.0, 2.0, -1.0, 1.0]
            self._next_spawn_step = 150
        self.traffic: list[Car] = []
        if self.mode == "race":
            for i in range(self.traffic_count):
                x = (100 + (i + 1) * 10) % self.track.width
                if i < 3:
                    spd = self.rng.uniform(5.0, 7.0)
                elif i < 5:
                    spd = self.rng.uniform(8.0, 10.0)
                else:
                    spd = self.rng.uniform(12.0, 15.0)
                y = self.track.height / 2 + self.rng.uniform(-1.0, 1.0)
                if i == 0:
                    self.traffic.append(CPUCar(x=x, y=y, target_speed=spd, rng=self.rng))
                else:
                    self.traffic.append(TrafficCar(x=x, y=y, target_speed=spd))

        # AI components for second car
        # Load GPT model lazily to avoid startup hiccups
        self.planner = GPTPlanner(autoload=False)  # High-level
        self.low_level = LowLevelController()
        self.learning_agent = LearningAgent()
        self.audio_volume = float(PARITY_CFG.get("audio_volume", 0.8))
        self.engine_volume = float(PARITY_CFG.get("engine_volume", self.audio_volume))
        self.voice_volume = float(PARITY_CFG.get("voice_volume", 1.0))
        self.effects_volume = float(PARITY_CFG.get("effects_volume", self.audio_volume))
        self.engine_pan_spread = float(PARITY_CFG.get("engine_pan_spread", 0.8))

        # Action space for Car 0 when controlled by a human or AI.
        # throttle: 0..1, brake: 0..1, steer: [-1,1]
        self.action_space = gym.spaces.Dict(
            {
                "throttle": gym.spaces.Box(low=0.0, high=1.0, shape=()),
                "brake": gym.spaces.Box(low=0.0, high=1.0, shape=()),
                "steer": gym.spaces.Box(low=-1.0, high=1.0, shape=()),
            }
        )

        # Observations: (car0_x, car0_y, car0_speed, car1_x, car1_y, car1_speed, remaining_time)
        high = np.array(
            [
                self.track.width,
                self.track.height,
                self.cars[0].max_speed,
                self.track.width,
                self.track.height,
                self.cars[1].max_speed,
                999.0,
            ]
            + [self.track.width, self.track.height] * 5,
            dtype=np.float32,
        )
        low = np.array([0.0] * (7 + 10), dtype=np.float32)
        self.k_traffic = 5
        self.observation_space = gym.spaces.Box(low, high, shape=(7 + 10,), dtype=np.float32)

        self.remaining_time = self.time_limit
        self.qualifying_time = None
        self.passes = 0
        self.crashes = 0
        self.crash_timer = 0.0
        self.safe_point = (50.0, 50.0)
        self.offroad_frames = 0
        self.slipstream_frames = 0
        self.slipstream_timer = 0.0
        self.skid_timer = 0.0
        self.start_timer = 0.0
        self.start_phase = "READY"
        self.lap = 0
        self.score = 0.0
        # Cumulative reward for the current episode
        self.episode_reward: float = 0.0
        self.overtakes = 0
        self.prev_progress = 0.0
        self.prev_x = 0.0
        self.prev_y = 0.0

        self.lap_timer = 0.0
        self.last_lap_time = None
        self.lap_flash = 0.0
        self.time_extend_flash = 0.0
        self.lap_times: list[float] = []
        self.grid_order: list[int] = []

        # Flag whether a lap completed this frame for timer grace
        self.lap_extended = False
        if self.mode == "qualify":
            self.game_message = "PREPARE TO QUALIFY"
        else:
            self.game_message = "PREPARE TO RACE"
        self.message_timer = 60.0
        self.invulnerable_timer = 0.0

        # Performance metrics
        self.plan_durations: list[float] = []
        self.plan_tokens: list[int] = []
        self.step_durations: list[float] = []
        self.ai_offtrack = 0
        # Per-step metrics for benchmarking
        self.step_log: list[dict] = []

        self.audio_stream = None
        self.engine_channel = None
        base = Path(__file__).resolve().parent.parent.parent / "assets" / "audio"
        gen_path = base / "generate_placeholders.py"
        gen_mod = None
        if gen_path.exists():
            spec = importlib.util.spec_from_file_location("audio_gen", gen_path)
            if spec and spec.loader:
                gen_mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(gen_mod)
                if hasattr(gen_mod, "generate_all"):
                    try:
                        gen_mod.generate_all(base)
                    except Exception:
                        pass
        def _load_audio(name: str, func_name: str | None, volume: float) -> "pg_mixer.Sound | None":
            if pg_mixer is None:
                return None
            path = base / name
            if path.exists() and path.stat().st_size > 0:
                try:
                    snd = pg_mixer.Sound(str(path))
                    snd.set_volume(volume)
                    return snd
                except Exception:
                    pass
            if gen_mod and func_name and hasattr(gen_mod, func_name):
                try:
                    if not pg_mixer.get_init():
                        pg_mixer.init(frequency=gen_mod.SAMPLE_RATE)
                    data = getattr(gen_mod, func_name)()
                    arr = np.ascontiguousarray(data * 32767, dtype=np.int16)
                    snd = pygame.sndarray.make_sound(arr)
                    snd.set_volume(volume)
                    return snd
                except Exception:
                    return None
            return None

        if pg_mixer is not None:
            try:
                if not pg_mixer.get_init():
                    pg_mixer.init()
                pg_mixer.music.set_volume(self.audio_volume)
            except Exception:
                pass

        self.crash_wave = _load_audio("crash.wav", "crash", self.effects_volume)
        self.skid_wave = _load_audio("skid.wav", "skid", self.effects_volume)
        self.prepare_qualify_wave = _load_audio("prepare_qualify.wav", "prepare_qualify_voice", self.voice_volume)
        self.prepare_race_wave = _load_audio("prepare_race.wav", "prepare_race_voice", self.voice_volume)
        self.final_lap_wave = _load_audio("final_lap.wav", "final_lap_voice", self.voice_volume)
        self.goal_wave = _load_audio("goal.wav", "goal_voice", self.voice_volume)
        self.checkpoint_wave = _load_audio("checkpoint.wav", "checkpoint", self.effects_volume)
        self.shift_wave = _load_audio("shift.wav", "shift_click", self.effects_volume)
        self.bgm_wave = _load_audio("bgm.wav", "bgm_theme", self.effects_volume)
        self.current_step = 0
        self.max_steps = 500  # limit episode length
        if FAST_TEST:
            self.max_steps = 50

        # pygame-related attributes (initialized lazily)
        self.screen = None
        self.clock = None
        self._scale = 3  # pixels per track unit
        self.renderer = None

    def configure_planner(self) -> None:
        """Prompt the player to load the GPT planner on demand."""

        print("Load GPT model? [y/N]", flush=True)
        ans = input().strip().lower()
        if ans.startswith("y"):
            try:
                self.planner.load_model()
                print("Model loaded!", flush=True)
            except Exception as exc:  # pragma: no cover - runtime error
                print(f"Load failed: {exc}", flush=True)


    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        _seed_all(seed)
        print("[ENV] Resetting environment", flush=True)
        self.rng = Random(seed)
        self.np_rng = np.random.default_rng(seed)
        # Keep track hash deterministic after resets
        self.track._hash = self.track._compute_hash()
        self.current_step = 0
        self.remaining_time = self.time_limit
        self.qualifying_time = None
        self.crash_timer = 0.0
        self.offroad_frames = 0
        self.slipstream_frames = 0
        self.slipstream_timer = 0.0
        self.skid_timer = 0.0
        self.last_steer = 0.0
        self.start_timer = 5.0 if self.mode == "race" else 0.0
        self.start_phase = "READY"
        self.lap = 0
        self.score = 0.0
        self.episode_reward = 0.0
        self.overtakes = 0
        self.prev_progress = 0.0
        self.prev_x = 0.0
        self.prev_y = 0.0

        self.lap_timer = 0.0
        self.last_lap_time = None
        self.lap_flash = 0.0
        self.time_extend_flash = 0.0
        self.lap_times = []
        self.grid_order = []
        self.lap_extended = False
        self._start_pos_shown = False
        self.game_message = ""
        self.message_timer = 0.0

        # Reset cars to start positions
        self.cars[0].x = 50.0
        self.cars[0].y = self.track.y_at(self.cars[0].x)
        self.cars[0].angle = 0.0
        self.cars[0].speed = 0.0
        self.track.start_x = self.cars[0].x
        self.safe_point = (self.cars[0].x, self.cars[0].y)

        self.cars[1].x = 150.0
        self.cars[1].y = self.track.y_at(self.cars[1].x)
        self.cars[1].angle = 0.0
        self.cars[1].speed = 0.0

        # Recompute track hash after state reset for determinism
        self.track._hash = self.track._compute_hash()

        if self.mode == "race":
            for i, t in enumerate(self.traffic):
                t.x = (100 + (i + 1) * 10) % self.track.width
                if i < 3:
                    t.target_speed = self.rng.uniform(5.0, 7.0)
                elif i < 5:
                    t.target_speed = self.rng.uniform(8.0, 10.0)
                else:
                    t.target_speed = self.rng.uniform(12.0, 15.0)
                t.y = self.track.height / 2 + self.rng.uniform(-1.0, 1.0)
                t.speed = 0.0
                t.prev_x = t.x

        self.prev_x = self.cars[0].x
        self.prev_y = self.cars[0].y
        self.prev_progress = self.track.progress(self.cars[0])

        self._play_prepare_voice()
        self._play_bgm_loop()

        # Clear per-step log
        self.step_log = []

        # Return initial observation
        obs = self._get_obs()
        info = {"track_hash": self.track.track_hash}
        return obs, info

    def step(self, action):
        """
        Step the environment.

        ``action`` can be either the old discrete form (0=throttle, 1=brake,
        2=no-op) or a tuple/dict specifying ``throttle``, ``brake`` and
        ``steer`` values.  This keeps backwards compatibility while enabling
        richer human control.
        Car 1 is AI-driven using GPT plan + LowLevelController.
        """
        step_start = time.perf_counter()
        if FAST_TEST:
            self.time_limit = min(self.time_limit, 20.0)
            self.traffic_count = 2
            if len(self.traffic) > self.traffic_count:
                self.traffic = self.traffic[: self.traffic_count]
        self.current_step += 1
        if getattr(self, "mode_2600", False) and self.current_step >= getattr(self, "_next_spawn_step", 0):
            idx = ((self.current_step - self._next_spawn_step) // 150) % len(self._2600_offsets)
            y = self.track.height / 2 + self._2600_offsets[idx]
            x = (100 + self.current_step) % self.track.width
            self.traffic.append(TrafficCar(x=x, y=y, target_speed=8.0))
            self._next_spawn_step += 150
        dt = 1.0 / self.metadata.get("render_fps", 60)
        if FAST_TEST:
            dt = 1.0
        if self.clock is not None:
            try:
                ms = self.clock.get_time()
                dt = ms / 1000.0 if ms > 0 else dt
            except Exception:
                pass
        self.remaining_time = max(self.remaining_time - dt, 0.0)

        # Reset lap extension flag each frame
        self.lap_extended = False
        self.lap_timer += dt
        if self.lap_flash > 0.0:
            self.lap_flash = max(self.lap_flash - dt, 0.0)
        if self.time_extend_flash > 0.0:
            self.time_extend_flash = max(self.time_extend_flash - dt, 0.0)
        if self.skid_timer > 0:
            self.skid_timer = max(self.skid_timer - dt, 0.0)
        if self.invulnerable_timer > 0:
            self.invulnerable_timer = max(self.invulnerable_timer - dt, 0.0)
        prev_obs = self._get_obs()
        reward = 0.0

        throttle, brake, steer, gear_cmd = 0.0, 0.0, 0.0, 0
        if isinstance(action, (tuple, list)):
            if len(action) >= 3:
                throttle, brake, steer = (
                    float(action[0]),
                    float(action[1]),
                    float(action[2]),
                )
            if len(action) >= 4:
                gear_cmd = int(action[3])
        elif isinstance(action, dict):
            throttle = float(action.get("throttle", 0.0))
            brake = float(action.get("brake", 0.0))
            steer = float(action.get("steer", 0.0))
            gear_cmd = int(action.get("gear", 0))
        else:
            if action == 0:
                throttle = True
            elif action == 1:
                brake = True
            # else action==2 => no action

        control_active = bool(throttle) or bool(brake)

        if self.crash_timer <= 0:
            for t in self.traffic:
                dx = (
                    (t.x - self.cars[0].x + self.track.width / 2) % self.track.width
                    - self.track.width / 2
                )
                if (
                    abs(dx) <= Car.length * 0.75
                    and abs(t.y - self.cars[0].y) <= Car.width / 2
                    and (control_active or abs(dx) < 0.1)
                ):

                    self.crashes += 1
                    self.crash_timer = 2.5
                    self._play_crash_audio()
                    self.cars[0].crash()
                    print("[ENV] Crash!", flush=True)
                    return self._get_obs(), -10.0, False, False, {}

        # Start light sequence (does not block motion in tests)
        if self.start_timer > 0:
            self.start_timer -= dt
            if self.start_timer >= 2.0:
                self.start_phase = "READY"
            elif self.start_timer > 0:
                self.start_phase = "SET"
            else:
                self.start_phase = "GO"
                print("[ENV] GO!", flush=True)
        elif (
            self.mode == "race"
            and self.start_position is not None
            and not self._start_pos_shown
        ):
            self.game_message = f"START POSITION {ordinal(self.start_position)}"
            self.message_timer = 90.0
            self._start_pos_shown = True
        if self.message_timer > 0:
            self.message_timer -= dt

        shifted = self.cars[0].shift(gear_cmd)
        if shifted:
            self._play_shift_audio()
            self.game_message = "HIGH" if gear_cmd > 0 else "LOW"
            self.message_timer = 1.0
        self.cars[0].apply_controls(throttle, brake, steer, dt=dt, track=self.track)
        self.last_steer = steer

        if self.mode == "race":
            # ---- Car 1 (AI) ----
            state_dict = {
                "x": self.cars[1].x,
                "y": self.cars[1].y,
                "speed": self.cars[1].speed,
            }
            plan_start = time.perf_counter()
            plan_text = self.planner.generate_plan(state_dict)
            self.plan_durations.append(time.perf_counter() - plan_start)
            self.plan_tokens.append(len(plan_text.strip().split()))

            tokens = plan_text.strip().split()
            try:
                target_speed = float(tokens[-1])
            except ValueError:
                target_speed = self.cars[1].speed

            dx = self.cars[0].x - self.cars[1].x
            dy = self.cars[0].y - self.cars[1].y
            dx = (dx + self.track.width / 2) % self.track.width - self.track.width / 2
            dy = (
                dy + self.track.height / 2
            ) % self.track.height - self.track.height / 2
            target_angle = np.arctan2(dy, dx)
            heading_error = (
                (target_angle - self.cars[1].angle + np.pi) % (2 * np.pi)
            ) - np.pi

            throttle_ai, brake_ai, steer_ai = self.low_level.compute_controls(
                self.cars[1].speed,
                target_speed,
                heading_error=heading_error,
            )
            self.cars[1].apply_controls(
                throttle_ai,
                brake_ai,
                steer_ai,
                dt=dt,
                track=self.track,
            )
            if self.cars[1].y < 5 or self.cars[1].y > self.track.height - 5:
                self.ai_offtrack += 1

            for t in self.traffic:
                if isinstance(t, CPUCar):
                    t.update(dt, self.track, self.cars[0])
                    th, br, steer_ai = t.policy(track=self.track)
                else:
                    th, br, steer_ai = t.policy(track=self.track)
                t.apply_controls(th, br, steer_ai, dt=dt, track=self.track)
                self.track.wrap_position(t)

        # Wrap positions on the track
        for c in self.cars:
            self.track.wrap_position(c)
        if self.cars[0].y < 0.0 or self.cars[0].y > self.track.height:
            if self.crash_timer <= 0:
                self.crashes += 1
                self.crash_timer = 2.5
                self.cars[0].crash()

        # Off-road penalty when leaving paved surface
        if not self.track.on_road(self.cars[0]):
            cap = 36.0  # ~80 MPH
            if self.cars[0].speed > cap:
                self.cars[0].speed = max(
                    cap,
                    self.cars[0].speed - self.cars[0].acceleration * dt,
                )
            self.offroad_frames += 1
            if self.offroad_frames > 30 and self.crash_timer <= 0:
                self.crashes += 1
                self.crash_timer = 2.5
                self.cars[0].crash()
        else:
            self.offroad_frames = 0

        if self.track.in_puddle(self.cars[0]):
            factor = self.track.get_puddle_factor()
            jitter = PARITY_CFG["puddle"].get("angle_jitter", 0.2)
            self.cars[0].speed *= factor
            self.cars[0].angle += self.np_rng.uniform(-jitter, jitter)

        if self.track.billboard_hit(self.cars[0]):
            self.remaining_time = max(self.remaining_time - 5.0, 0.0)
            self._play_crash_audio()
            if self.crash_timer <= 0:
                self.crashes += 1
                self.crash_timer = 2.5
                self.cars[0].crash()

        # Slip-angle skid penalty
        if abs(steer) > 0.7 and self.cars[0].speed > 5:
            self.cars[0].speed *= 0.95
            self.skid_timer = 1.0
            self._play_skid_audio()

        if self.slipstream_enabled:
            slip = False
            for other in [self.cars[1]] + self.traffic:
                dx = (other.x - self.cars[0].x + self.track.width) % self.track.width
                dy = abs(other.y - self.cars[0].y)
                if 0 < dx <= 3.0 and dy < 1.0:
                    slip = True
                    break
            if slip:
                self.slipstream_timer += dt
                if self.slipstream_timer >= 0.5:
                    self.cars[0].speed = min(
                        self.cars[0].speed * 1.05,
                        self.cars[0].gear_max[self.cars[0].gear] + 5,
                    )
                    self.slipstream_frames += 1
                    self.slipstream_timer = 0.0
            else:
                self.slipstream_timer = 0.0
        else:
            self.slipstream_timer = 0.0

        if self.crash_timer > 0:
            self.crash_timer -= dt
            if self.crash_timer <= 0:
                self.cars[0].x, self.cars[0].y = self.safe_point
                self.cars[0].speed = 0.0
                self.invulnerable_timer = 0.5
        else:
            self.safe_point = (self.cars[0].x, self.cars[0].y)
            if self.invulnerable_timer <= 0:
                pass

        # Binaural audio: generate waveform based on each car's speed
        self._play_binaural_audio()

        # Scoring distance and overtakes
        dist = float(
            ((self.cars[0].x - self.prev_x) ** 2 + (self.cars[0].y - self.prev_y) ** 2)
            ** 0.5
        )
        self.score += dist * 50
        for t in self.traffic:
            if (
                hasattr(t, "prev_x")
                and self.prev_x < t.prev_x <= self.cars[0].x
                and abs(self.cars[0].y - t.y) < 1.0
            ):
                self.overtakes += 1
                self.score += 50
            t.prev_x = t.x

        progress = self.track.progress(self.cars[0])
        if progress < self.prev_progress:
            self.lap += 1
            self.score += 2000
            self.last_lap_time = self.lap_timer
            self.lap_times.append(self.lap_timer)
            self.lap_timer = 0.0
            self.lap_flash = 2.0
            self.remaining_time += 30.0
            self.lap_extended = True
            self.time_extend_flash = 2.0
            self._play_checkpoint_audio()
            print(f"[ENV] Completed lap {self.lap} in {self.last_lap_time:.2f}s", flush=True)
            try:
                submit_lap_time_http(
                    self.player_name, int(self.last_lap_time * 1000)
                )
            except Exception:
                pass
            if self.mode == "qualify":
                self.grid_order = sorted(
                    range(len(self.cars)),
                    key=lambda i: (
                        self.lap_times[i] if i < len(self.lap_times) else float("inf")
                    ),
                )
            if self.lap == 3:
                self._play_final_lap_voice()

        if self.mode == "race":
            pass

        self.prev_progress = progress
        self.prev_x = self.cars[0].x
        self.prev_y = self.cars[0].y
        done = False
        if self.mode == "qualify":
            elapsed = (self.time_limit - self.remaining_time)
            reward = progress - 0.1 * elapsed
            if progress >= 1.0:
                self.qualifying_time = elapsed
                self.qualifying_rank, bonus = _qualifying_bonus(elapsed)
                self.score += bonus
                self.game_message = f"QUALIFIED {ordinal(self.qualifying_rank)}"
                self.message_timer = 90.0
                done = True
        else:  # race
            reward = self.cars[0].speed * 0.05

        if self.mode == "race":
            dist = self.track.distance(self.cars[0], self.cars[1])
            if dist < 5.0:
                reward -= 1.0

        if self.mode == "race" and self.lap >= 4:
            done = True
            self._play_goal_voice()
            self.game_message = "FINISHED!"
            self.message_timer = 90.0

        if self.remaining_time <= 0 and not self.lap_extended:
            done = True
            self.game_message = "TIME UP!"
            self.message_timer = 90.0
        done = done or (self.current_step >= self.max_steps)

        # Record per-step metrics
        self.step_log.append(
            {
                "step": self.current_step,
                "car0_x": self.cars[0].x,
                "car0_y": self.cars[0].y,
                "car0_speed": self.cars[0].speed,
                "car1_x": self.cars[1].x,
                "car1_y": self.cars[1].y,
                "car1_speed": self.cars[1].speed,
                "reward": reward,
                "remaining_time": self.remaining_time,
                "lap": self.lap,
            }
        )
        if done:
            try:
                from ..evaluation.logger import log_episode

                log_episode(self)
            except Exception:
                pass
            self.score += int(self.remaining_time * 5)
            try:
                submit_score_http(self.player_name, int(self.score))
            except Exception:
                pass
            print("[ENV] Race finished", flush=True)

        obs = self._get_obs()
        experience = (prev_obs, action, reward, obs)
        self.learning_agent.update_on_experience([experience])
        self.step_durations.append(time.perf_counter() - step_start)
        info = {"track_hash": self.track.track_hash}
        return obs, reward, done, False, info

    def render(self) -> None:
        """Render the environment."""
        global pygame
        if self.render_mode != "human":
            return

        if pygame is None:
            # Fallback textual render
            print(
                f"Car0: ({self.cars[0].x:.2f}, {self.cars[0].y:.2f}) "
                f"Spd={self.cars[0].speed:.2f} | "
                f"Car1: ({self.cars[1].x:.2f}, {self.cars[1].y:.2f}) "
                f"Spd={self.cars[1].speed:.2f}"
            )
            return

        if self.screen is None:
            try:
                pygame.init()
                size = (256, 224)
                self.screen = pygame.display.set_mode(size)
                pygame.display.set_caption("Super Pole Position")
                self.clock = pygame.time.Clock()
                self.renderer = Pseudo3DRenderer(self.screen)
            except Exception as exc:  # pragma: no cover - init error
                if os.name != "nt" and "DISPLAY" not in os.environ:
                    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
                    try:
                        pygame.init()
                        size = (256, 224)
                        self.screen = pygame.display.set_mode(size)
                        pygame.display.set_caption("Super Pole Position")
                        self.clock = pygame.time.Clock()
                        self.renderer = Pseudo3DRenderer(self.screen)
                    except Exception as exc2:
                        print(f"pygame init failed: {exc2}", flush=True)
                        self.screen = None
                        pygame = None
                        return
                else:
                    print(f"pygame init failed: {exc}", flush=True)
                    self.screen = None
                    pygame = None
                    return

        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.close()
                    return
                if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                    self.configure_planner()
        except Exception as exc:  # pragma: no cover - event error
            print(f"pygame event error: {exc}", flush=True)
            return

        try:
            if self.renderer:
                self.renderer.draw(self)
            else:
                self._render_fallback()
            pygame.display.flip()
            if self.clock:
                self.clock.tick(self.metadata.get("render_fps", 30))
        except Exception as exc:  # pragma: no cover - render error
            print(f"render failure: {exc}", flush=True)
            self.close()

    def _render_fallback(self) -> None:
        """Draw a simple top-down view if arcade renderer is unavailable."""

        self.screen.fill((0, 0, 0))
        pygame.draw.rect(
            self.screen,
            (50, 50, 50),
            pygame.Rect(
                0,
                0,
                self.track.width * self._scale,
                self.track.height * self._scale,
            ),
            2,
        )
        for p in getattr(self.track, "puddles", []):
            x = int(p.x * self._scale)
            y = int(p.y * self._scale)
            r = max(1, int(p.radius * self._scale))
            pygame.draw.circle(self.screen, (40, 40, 120), (x, y), r)
        colors = [(255, 0, 0), (0, 255, 0)]
        for car, color in zip(self.cars, colors):
            x = int(car.x * self._scale)
            y = int(car.y * self._scale)
            pygame.draw.circle(self.screen, color, (x, y), 5)

    def _play_binaural_audio(self, duration=0.1, sample_rate=44100):
        """Generate stereo engine audio with per-player panning."""
        if pg_mixer is None or pygame is None:
            return

        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

        def engine_wave(freq):
            wobble = 0.02 * np.sin(2 * np.pi * 8 * t)
            mod_freq = freq * (1.0 + wobble)
            base = 0.3 * np.sin(2 * np.pi * mod_freq * t)
            harm2 = 0.2 * np.sin(2 * np.pi * mod_freq * 2 * t)
            harm3 = 0.1 * np.sin(2 * np.pi * mod_freq * 3 * t)
            rumble = 0.05 * self.np_rng.uniform(-1.0, 1.0, len(t))
            return base + harm2 + harm3 + rumble

        freq0 = engine_pitch(self.cars[0].rpm(), self.cars[0].gear)
        freq1 = engine_pitch(self.cars[1].rpm(), self.cars[1].gear)

        wave0 = engine_wave(freq0)
        wave1 = engine_wave(freq1)

        spread = max(0.0, min(1.0, self.engine_pan_spread))
        left0_gain = 0.5 + 0.5 * spread
        right0_gain = 0.5 - 0.5 * spread
        left1_gain = 0.5 - 0.5 * spread
        right1_gain = 0.5 + 0.5 * spread

        left = wave0 * left0_gain + wave1 * left1_gain
        right = wave0 * right0_gain + wave1 * right1_gain

        waveform = np.vstack((left, right)).T
        waveform = np.clip(waveform, -1.0, 1.0)
        waveform_int16 = np.ascontiguousarray(waveform * 32767, dtype=np.int16)

        if self.engine_channel is not None:
            try:
                self.engine_channel.stop()
            except Exception:
                pass

        if not pg_mixer.get_init():
            try:
                pg_mixer.init(frequency=sample_rate, channels=2)
            except Exception:
                return
        sound = pygame.sndarray.make_sound(waveform_int16)
        channel = sound.play()
        if channel:
            channel.set_volume(self.engine_volume, self.engine_volume)
        self.engine_channel = channel

    def _play_crash_audio(self) -> None:
        """Play crash sound effect once."""

        if pg_mixer is None:
            return
        if self.crash_wave is None:
            return
        pan = (self.cars[0].x - self.track.width / 2) / (self.track.width / 2)
        self._play_panned_wave(self.crash_wave, pan, self.effects_volume)

    def _play_prepare_voice(self) -> None:
        """Play the appropriate 'Prepare' voice sample."""

        if pg_mixer is None:
            return
        wave_obj = (
            self.prepare_qualify_wave
            if self.mode == "qualify"
            else self.prepare_race_wave
        )
        if wave_obj is None:
            return
        try:
            wave_obj.play()
        except Exception:  # pragma: no cover
            pass

    def _play_bgm_loop(self) -> None:
        """Start looping background music playback."""

        if os.environ.get("MUTE_BGM", "0") == "1":
            return
        if pg_mixer is None or self.bgm_wave is None:
            return
        try:
            self.bgm_wave.play(loops=-1)
        except Exception:  # pragma: no cover
            pass

    def _play_final_lap_voice(self) -> None:
        """Play 'Final Lap' voice sample."""

        if pg_mixer is None:
            return
        if self.final_lap_wave is None:
            return
        try:
            self.final_lap_wave.play()
        except Exception:  # pragma: no cover
            pass

    def _play_goal_voice(self) -> None:
        """Play 'Goal' voice sample when race finishes."""

        if pg_mixer is None:
            return
        if self.goal_wave is None:
            return
        try:
            self.goal_wave.play()
        except Exception:  # pragma: no cover
            pass

    def _play_panned_wave(self, wave_obj, pan: float, volume: float) -> None:
        """Play ``wave_obj`` panned left/right using ``volume`` (-1..1 pan)."""

        if pg_mixer is None:
            return
        if wave_obj is None:
            return
        try:
            if not pg_mixer.get_init():
                try:
                    pg_mixer.init()
                except Exception:
                    return
            pan = max(-1.0, min(1.0, pan))
            channel = wave_obj.play()
            if channel:
                channel.set_volume(
                    volume * (1.0 - max(0.0, pan)),
                    volume * (1.0 + min(0.0, pan)),
                )
            self.audio_stream = channel
        except Exception:  # pragma: no cover
            try:
                wave_obj.play()
            except Exception:
                pass

    def _play_skid_audio(self) -> None:
        """Play short noise burst when skidding with stereo pan."""

        if pg_mixer is None:
            return
        if self.skid_wave is not None:
            pan = (self.cars[0].x - self.track.width / 2) / (self.track.width / 2)
            self._play_panned_wave(self.skid_wave, pan, self.effects_volume)
            return

        duration = 0.2
        sample_rate = 44100
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        noise = self.np_rng.uniform(-1.0, 1.0, len(t))
        pan = (self.cars[0].x - self.track.width / 2) / (self.track.width / 2)
        pan = max(-1.0, min(1.0, pan))
        left = 0.3 * noise * (1.0 - max(0.0, pan))
        right = 0.3 * noise * (1.0 + min(0.0, pan))
        waveform = np.vstack((left, right)).T
        waveform_int16 = np.ascontiguousarray(waveform * 32767, dtype=np.int16)
        if self.audio_stream is not None:
            try:
                self.audio_stream.stop()
            except Exception:
                pass
        if not pg_mixer.get_init():
            try:
                pg_mixer.init(frequency=sample_rate, channels=2)
            except Exception:
                return
        sound = pygame.sndarray.make_sound(waveform_int16)
        self.audio_stream = sound.play()

    def _play_checkpoint_audio(self) -> None:
        """Play checkpoint chime when time extends."""

        if pg_mixer is None:
            return
        if self.checkpoint_wave is None:
            return
        try:
            self.checkpoint_wave.play()
        except Exception:  # pragma: no cover
            pass

    def _play_shift_audio(self) -> None:
        """Play a short click when shifting gears."""

        if pg_mixer is None or self.shift_wave is None:
            return
        try:
            self.shift_wave.play()
        except Exception:  # pragma: no cover - audio may fail
            pass

    def close(self):
        """Clean up resources like audio streams."""
        if self.audio_stream is not None:
            try:
                self.audio_stream.stop()
            except Exception:
                pass
            self.audio_stream = None
        if self.engine_channel is not None:
            try:
                self.engine_channel.stop()
            except Exception:
                pass
            self.engine_channel = None

        if pg_mixer is not None:
            try:
                pg_mixer.quit()
            except Exception:
                pass

        if pygame is not None and self.screen is not None:
            pygame.quit()
            self.screen = None

    def _get_obs(self):
        """Return observation array including nearest traffic cars."""
        base = [
            self.cars[0].x,
            self.cars[0].y,
            self.cars[0].speed,
            self.cars[1].x,
            self.cars[1].y,
            self.cars[1].speed,
            self.remaining_time,
        ]
        traffic_rel = []
        if self.traffic:
            dists = [self.track.distance(self.cars[0], t) for t in self.traffic]
            ordered = [
                t for _, t in sorted(zip(dists, self.traffic), key=lambda p: p[0])
            ]
            for t in ordered[: self.k_traffic]:
                dx = t.x - self.cars[0].x
                dy = t.y - self.cars[0].y
                traffic_rel.extend([dx, dy])
        while len(traffic_rel) < 2 * self.k_traffic:
            traffic_rel.extend([0.0, 0.0])
        return np.array(base + traffic_rel, dtype=np.float32)
