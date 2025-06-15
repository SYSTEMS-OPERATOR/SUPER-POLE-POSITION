#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 MIND INTERFACES, INC. All rights reserved.
# Licensed under the MIT License.

"""
pole_position.py
Description: Module for Super Pole Position.
"""

import os
import numpy as np
import gymnasium as gym
import time
from pathlib import Path

try:
    import pygame  # optional dependency for graphics
    from pygame import mixer as pg_mixer  # audio fallback via pygame
except Exception:  # pragma: no cover - optional dependency may be missing
    pygame = None
    pg_mixer = None
try:
    import simpleaudio as sa
except Exception:  # pragma: no cover - optional dependency
    sa = None

from ..physics.car import Car
from ..physics.track import Track
from ..physics.traffic_car import TrafficCar
from ..agents.controllers import GPTPlanner, LowLevelController, LearningAgent
from ..ui.arcade import Pseudo3DRenderer

from ..config import load_parity_config
from ..config import load_arcade_parity

_PARITY_CONFIG = load_arcade_parity()
ENGINE_BASE_FREQ = _PARITY_CONFIG.get("engine_base_freq", 400.0)
ENGINE_PITCH_FACTOR = _PARITY_CONFIG.get("engine_pitch_factor", 3000.0)


def engine_pitch(rpm: float) -> float:
    """Return engine frequency in Hz for ``rpm`` (0..1)."""

    return ENGINE_BASE_FREQ + ENGINE_PITCH_FACTOR * rpm

FAST_TEST = bool(int(os.getenv("FAST_TEST", "0")))
PARITY_CFG = load_parity_config()


class PolePositionEnv(gym.Env):
    """
    A multi-car racing environment with:
    - Toroidal 2D track
    - Binaural audio based on each car's speed
    - GPT-based high-level plan for Car B
    - A single discrete action for Car A (player or random)
    - Optional hyper mode for uncapped speed
    """

    metadata = {"render_modes": ["human"], "render_fps": 30}

    def __init__(
        self,
        render_mode: str = "human",
        mode: str = "race",
        track_name: str | None = None,
        hyper: bool = False,
    ) -> None:
        """Create a Pole Position environment.

        :param render_mode: ``human`` for pygame output.
        :param mode: ``race`` or ``qualify``.
        :param track_name: Optional track to load.
        :param hyper: If ``True`` doubles gear limits for extreme speed.
        """

        super().__init__()
        self.render_mode = render_mode
        self.mode = mode
        self.hyper = hyper

        self.time_limit = 90.0 if self.mode == "race" else 73.0
        self.traffic_count = 7 if self.mode == "race" else 0
        if FAST_TEST:
            self.time_limit = min(self.time_limit, 5.0)
            self.traffic_count = 2

        # Track & cars
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
        self.traffic: list[TrafficCar] = []
        if self.mode == "race":
            for i in range(self.traffic_count):
                x = (i * 10) % self.track.width
                speed = 5.0 + (i % 3)
                self.traffic.append(
                    TrafficCar(x=x, y=self.track.height / 2, target_speed=speed)
                )

        # AI components for second car
        self.planner = GPTPlanner()  # High-level
        self.low_level = LowLevelController()
        self.learning_agent = LearningAgent()

        # Action space for Car 0 when controlled by a human or AI.
        # throttle: {0,1}, brake: {0,1}, steer: [-1,1]
        self.action_space = gym.spaces.Dict(
            {
                "throttle": gym.spaces.Discrete(2),
                "brake": gym.spaces.Discrete(2),
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
        self.observation_space = gym.spaces.Box(
            low, high, shape=(7 + 10,), dtype=np.float32
        )
        self.remaining_time = self.time_limit
        self.next_checkpoint = 0.25
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
        self.overtakes = 0
        self.prev_progress = 0.0
        self.prev_x = 0.0
        self.prev_y = 0.0

        self.lap_timer = 0.0
        self.last_lap_time = None
        self.lap_flash = 0.0
        self.lap_times: list[float] = []
        self.grid_order: list[int] = []

        # Performance metrics
        self.plan_durations: list[float] = []
        self.plan_tokens: list[int] = []
        self.step_durations: list[float] = []
        self.ai_offtrack = 0
        # Per-step metrics for benchmarking
        self.step_log: list[dict] = []

        self.audio_stream = None
        base = Path(__file__).resolve().parent.parent / "assets" / "audio"
        if sa is not None:
            try:
                # Audio files are expected under assets/audio/ but may be absent
                # in open-source releases.  They will be provided separately.
                self.crash_wave = sa.WaveObject.from_wave_file(str(base / "crash.wav"))
                self.prepare_wave = sa.WaveObject.from_wave_file(
                    str(base / "prepare.wav")
                )
                self.final_lap_wave = sa.WaveObject.from_wave_file(
                    str(base / "final_lap.wav")
                )
                self.goal_wave = sa.WaveObject.from_wave_file(str(base / "goal.wav"))
                self.bgm_wave = sa.WaveObject.from_wave_file(
                    str(base / "namco_theme.wav")
                )
            except Exception:  # pragma: no cover - file missing
                # Placeholders handle missing WAVs during tests
                self.crash_wave = None
                self.prepare_wave = None
                self.final_lap_wave = None
                self.goal_wave = None
                self.bgm_wave = None
        elif pg_mixer is not None:
            try:
                pg_mixer.init()
                self.crash_wave = pg_mixer.Sound(str(base / "crash.wav"))
                self.prepare_wave = pg_mixer.Sound(str(base / "prepare.wav"))
                self.final_lap_wave = pg_mixer.Sound(str(base / "final_lap.wav"))
                self.goal_wave = pg_mixer.Sound(str(base / "goal.wav"))
                self.bgm_wave = pg_mixer.Sound(str(base / "namco_theme.wav"))
            except Exception:  # pragma: no cover - file missing or mixer error
                self.crash_wave = None
                self.prepare_wave = None
                self.final_lap_wave = None
                self.goal_wave = None
                self.bgm_wave = None
        else:
            self.crash_wave = None
            self.prepare_wave = None
            self.final_lap_wave = None
            self.goal_wave = None
            self.bgm_wave = None
        self.current_step = 0
        self.max_steps = 500  # limit episode length

        # pygame-related attributes (initialized lazily)
        self.screen = None
        self.clock = None
        self._scale = 3  # pixels per track unit
        self.renderer = None

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.current_step = 0
        self.remaining_time = self.time_limit
        self.next_checkpoint = 0.25
        self.qualifying_time = None
        self.crash_timer = 0.0
        self.offroad_frames = 0
        self.slipstream_frames = 0
        self.slipstream_timer = 0.0
        self.skid_timer = 0.0
        self.start_timer = 5.0 if self.mode == "race" else 0.0
        self.start_phase = "READY"
        self.lap = 0
        self.score = 0.0
        self.overtakes = 0
        self.prev_progress = 0.0
        self.prev_x = 0.0
        self.prev_y = 0.0

        self.lap_timer = 0.0
        self.last_lap_time = None
        self.lap_flash = 0.0
        self.lap_times = []
        self.grid_order = []

        # Reset cars to start positions
        self.cars[0].x = 50.0
        self.cars[0].y = 50.0
        self.cars[0].angle = 0.0
        self.cars[0].speed = 0.0
        self.track.start_x = self.cars[0].x
        self.safe_point = (self.cars[0].x, self.cars[0].y)

        self.cars[1].x = 150.0
        self.cars[1].y = 150.0
        self.cars[1].angle = 0.0
        self.cars[1].speed = 0.0

        if self.mode == "race":
            for i, t in enumerate(self.traffic):
                t.x = (i * 10) % self.track.width
                t.y = self.track.height / 2
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
        return self._get_obs(), {}

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
            self.time_limit = min(self.time_limit, 5.0)
            self.traffic_count = 2
            if len(self.traffic) > self.traffic_count:
                self.traffic = self.traffic[: self.traffic_count]
        self.current_step += 1
        if self.current_step == 1:
            self.next_checkpoint = self.track.progress(self.cars[0]) + 0.25
        self.remaining_time = max(self.remaining_time - 1.0, 0.0)
        self.lap_timer += 1.0
        if self.lap_flash > 0.0:
            self.lap_flash = max(self.lap_flash - 1.0, 0.0)
        if self.skid_timer > 0:
            self.skid_timer = max(self.skid_timer - 1.0, 0.0)
        prev_obs = self._get_obs()
        reward = 0.0

        if self.crash_timer <= 0:
            for t in self.traffic:
                if (
                    abs(t.x - self.cars[0].x) < Car.length
                    and abs(t.y - self.cars[0].y) < Car.width / 2
                ):
                    self.crashes += 1
                    self.crash_timer = 2.5
                    self._play_crash_audio()
                    self.cars[0].crash()
                    return self._get_obs(), -10.0, False, False, {}

        # Start light sequence (does not block motion in tests)
        if self.start_timer > 0:
            self.start_timer -= 1.0
            if self.start_timer >= 2.0:
                self.start_phase = "READY"
            elif self.start_timer > 0:
                self.start_phase = "SET"
            else:
                self.start_phase = "GO"

        # ---- Car 0 (Player / Random) ----
        throttle, brake, steer, gear_cmd = False, False, 0.0, 0
        if isinstance(action, (tuple, list)):
            if len(action) >= 3:
                throttle, brake, steer = (
                    bool(action[0]),
                    bool(action[1]),
                    float(action[2]),
                )
            if len(action) >= 4:
                gear_cmd = int(action[3])
        elif isinstance(action, dict):
            throttle = bool(action.get("throttle", False))
            brake = bool(action.get("brake", False))
            steer = float(action.get("steer", 0.0))
            gear_cmd = int(action.get("gear", 0))
        else:
            if action == 0:
                throttle = True
            elif action == 1:
                brake = True
            # else action==2 => no action

        self.cars[0].shift(gear_cmd)
        dt = 1.0
        if self.clock is not None:
            try:
                ms = self.clock.get_time()
                dt = ms / 1000.0 if ms > 0 else 1.0 / self.metadata.get("render_fps", 30)
            except Exception:
                dt = 1.0 / self.metadata.get("render_fps", 30)
        self.cars[0].apply_controls(throttle, brake, steer, dt=dt, track=self.track)

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
                th, br, steer_ai = t.policy(track=self.track)
                t.apply_controls(th, br, steer_ai, dt=dt, track=self.track)
                self.track.wrap_position(t)

        # Wrap positions on the track
        for c in self.cars:
            self.track.wrap_position(c)

        # Off-road slowdown near track edges
        offroad = self.cars[0].y < 5 or self.cars[0].y > self.track.height - 5
        if offroad:
            self.cars[0].speed *= 0.5
            self.offroad_frames += 1

        if self.track.in_puddle(self.cars[0]):
            factor = PARITY_CFG["puddle"].get("speed_factor", 0.7)
            jitter = PARITY_CFG["puddle"].get("angle_jitter", 0.2)
            self.cars[0].speed *= factor
            self.cars[0].angle += np.random.uniform(-jitter, jitter)

        if self.track.billboard_hit(self.cars[0]):
            self.remaining_time = max(self.remaining_time - 5.0, 0.0)
            self._play_crash_audio()

        # Slip-angle skid penalty
        if abs(steer) > 0.7 and self.cars[0].speed > 5:
            self.cars[0].speed *= 0.95
            self.skid_timer = 1.0
            self._play_skid_audio()

        # Slipstream boost behind another car
        slip = False
        for other in [self.cars[1]] + self.traffic:
            dx = (other.x - self.cars[0].x + self.track.width) % self.track.width
            dy = abs(other.y - self.cars[0].y)
            if 0 < dx <= 3.0 and dy < 1.0:
                slip = True
                break
        if slip:
            self.slipstream_timer += 1.0
            if self.slipstream_timer >= 1.0:
                self.cars[0].speed = min(
                    self.cars[0].speed * 1.1,
                    self.cars[0].gear_max[self.cars[0].gear],
                )
                self.slipstream_frames += 1
        else:
            self.slipstream_timer = 0.0

        if self.crash_timer > 0:
            self.crash_timer -= 1.0
            if self.crash_timer <= 0:
                self.cars[0].x, self.cars[0].y = self.safe_point
                self.cars[0].speed = 0.0
        else:
            self.safe_point = (self.cars[0].x, self.cars[0].y)
            for t in self.traffic:
                if (
                    abs(t.x - self.cars[0].x) < Car.length
                    and abs(t.y - self.cars[0].y) < Car.width / 2
                ):
                    self.crashes += 1
                    self.crash_timer = 2.5
                    self._play_crash_audio()
                    self.cars[0].crash()
                    reward = -10.0
                    return self._get_obs(), reward, False, False, {}

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
            while progress >= self.next_checkpoint:
                self.remaining_time += 30.0
                self.next_checkpoint += 0.25
        self.prev_progress = progress
        self.prev_x = self.cars[0].x
        self.prev_y = self.cars[0].y
        done = False
        if self.mode == "qualify":
            elapsed = self.time_limit - self.remaining_time
            reward = progress - 0.1 * elapsed
            if progress >= 1.0:
                self.qualifying_time = elapsed
                if elapsed < 55.0:
                    self.score += 5000
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
        done = done or self.remaining_time <= 0 or (self.current_step >= self.max_steps)

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

        experience = (prev_obs, action, reward, self._get_obs())
        self.learning_agent.update_on_experience([experience])
        self.step_durations.append(time.perf_counter() - step_start)
        return self._get_obs(), reward, done, False, {}

    def render(self):
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
                size = (640, 480)
                self.screen = pygame.display.set_mode(size)
                pygame.display.set_caption("Super Pole Position")
                self.clock = pygame.time.Clock()
                self.renderer = Pseudo3DRenderer(self.screen)
            except Exception as exc:  # pragma: no cover - init error
                print(f"pygame init failed: {exc}", flush=True)
                self.screen = None
                pygame = None
                return

        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.close()
                    return
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
        colors = [(255, 0, 0), (0, 255, 0)]
        for car, color in zip(self.cars, colors):
            x = int(car.x * self._scale)
            y = int(car.y * self._scale)
            pygame.draw.circle(self.screen, color, (x, y), 5)

    def _play_binaural_audio(self, duration=0.1, sample_rate=44100):
        """Generate stereo engine audio with basic position-based panning."""
        if sa is None and pg_mixer is None:
            return

        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

        def engine_wave(freq):
            base = 0.3 * np.sin(2 * np.pi * freq * t)
            harm2 = 0.2 * np.sin(2 * np.pi * freq * 2 * t)
            harm3 = 0.1 * np.sin(2 * np.pi * freq * 3 * t)
            rumble = 0.05 * np.random.uniform(-1.0, 1.0, len(t))
            return base + harm2 + harm3 + rumble

        def panned_engine(car):
            freq = engine_pitch(car.rpm())
            pan = (car.y - self.track.height / 2) / (self.track.height / 2)
            pan = max(-1.0, min(1.0, pan))
            wave = engine_wave(freq)
            left_gain = 1.0 - max(0.0, pan)
            right_gain = 1.0 + min(0.0, pan)
            return wave * left_gain, wave * right_gain

        left0, right0 = panned_engine(self.cars[0])
        left1, right1 = panned_engine(self.cars[1])

        left = left0 + left1
        right = right0 + right1

        waveform = np.vstack((left, right)).T
        waveform = np.clip(waveform, -1.0, 1.0)
        waveform_int16 = np.int16(waveform * 32767)

        if self.audio_stream is not None:
            try:
                self.audio_stream.stop()
            except Exception:
                pass

        if sa is not None:
            self.audio_stream = sa.play_buffer(
                waveform_int16,
                num_channels=2,
                bytes_per_sample=2,
                sample_rate=sample_rate,
            )
        elif pg_mixer is not None:
            if not pg_mixer.get_init():
                try:
                    pg_mixer.init(frequency=sample_rate, channels=2)
                except Exception:
                    return
            sound = pygame.sndarray.make_sound(waveform_int16)
            self.audio_stream = sound.play()

    def _play_crash_audio(self) -> None:
        """Play crash sound effect once."""

        if sa is None and pg_mixer is None:
            return
        if self.crash_wave is None:
            return
        pan = (self.cars[0].x - self.track.width / 2) / (self.track.width / 2)
        self._play_panned_wave(self.crash_wave, pan)

    def _play_prepare_voice(self) -> None:
        """Play the 'Get Ready' voice sample."""

        if sa is None and pg_mixer is None:
            return
        if self.prepare_wave is None:
            return
        try:
            self.prepare_wave.play()
        except Exception:  # pragma: no cover
            pass

    def _play_bgm_loop(self) -> None:
        """Start background music playback once."""

        if sa is None and pg_mixer is None:
            return
        if self.bgm_wave is None:
            return
        try:
            # simpleaudio lacks looping support; play once per reset
            self.bgm_wave.play()
        except Exception:  # pragma: no cover
            pass

    def _play_final_lap_voice(self) -> None:
        """Play 'Final Lap' voice sample."""

        if sa is None and pg_mixer is None:
            return
        if self.final_lap_wave is None:
            return
        try:
            self.final_lap_wave.play()
        except Exception:  # pragma: no cover
            pass

    def _play_goal_voice(self) -> None:
        """Play 'Goal' voice sample when race finishes."""

        if sa is None and pg_mixer is None:
            return
        if self.goal_wave is None:
            return
        try:
            self.goal_wave.play()
        except Exception:  # pragma: no cover
            pass

    def _play_panned_wave(self, wave_obj, pan: float) -> None:
        """Play ``wave_obj`` panned left/right based on ``pan`` (-1..1)."""

        if sa is None and pg_mixer is None:
            return
        if wave_obj is None:
            return
        try:
            if sa is not None and hasattr(wave_obj, "audio_data"):
                audio = np.frombuffer(wave_obj.audio_data, dtype=np.int16)
                if wave_obj.num_channels == 1:
                    audio = np.repeat(audio, 2)
                audio = audio.reshape(-1, 2)
                pan = max(-1.0, min(1.0, pan))
                left_gain = 1.0 - max(0.0, pan)
                right_gain = 1.0 + min(0.0, pan)
                audio[:, 0] = (audio[:, 0] * left_gain).astype(np.int16)
                audio[:, 1] = (audio[:, 1] * right_gain).astype(np.int16)
                if self.audio_stream is not None:
                    self.audio_stream.stop()
                self.audio_stream = sa.play_buffer(
                    audio,
                    num_channels=2,
                    bytes_per_sample=wave_obj.bytes_per_sample,
                    sample_rate=wave_obj.sample_rate,
                )
            elif pg_mixer is not None:
                if not pg_mixer.get_init():
                    try:
                        pg_mixer.init()
                    except Exception:
                        return
                pan = max(-1.0, min(1.0, pan))
                channel = wave_obj.play()
                if channel:
                    channel.set_volume(1.0 - max(0.0, pan), 1.0 + min(0.0, pan))
                self.audio_stream = channel
        except Exception:  # pragma: no cover
            try:
                wave_obj.play()
            except Exception:
                pass

    def _play_skid_audio(self) -> None:
        """Play short noise burst when skidding with stereo pan."""

        if sa is None and pg_mixer is None:
            return
        duration = 0.2
        sample_rate = 44100
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        noise = np.random.uniform(-1.0, 1.0, len(t))
        pan = (self.cars[0].x - self.track.width / 2) / (self.track.width / 2)
        pan = max(-1.0, min(1.0, pan))
        left = 0.3 * noise * (1.0 - max(0.0, pan))
        right = 0.3 * noise * (1.0 + min(0.0, pan))
        waveform = np.vstack((left, right)).T
        waveform_int16 = np.int16(waveform * 32767)
        if self.audio_stream is not None:
            try:
                self.audio_stream.stop()
            except Exception:
                pass
        if sa is not None:
            self.audio_stream = sa.play_buffer(
                waveform_int16,
                num_channels=2,
                bytes_per_sample=2,
                sample_rate=sample_rate,
            )
        elif pg_mixer is not None:
            if not pg_mixer.get_init():
                try:
                    pg_mixer.init(frequency=sample_rate, channels=2)
                except Exception:
                    return
            sound = pygame.sndarray.make_sound(waveform_int16)
            self.audio_stream = sound.play()

    def close(self):
        """Clean up resources like audio streams."""
        if self.audio_stream is not None:
            try:
                self.audio_stream.stop()
            except Exception:
                pass
            self.audio_stream = None

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
