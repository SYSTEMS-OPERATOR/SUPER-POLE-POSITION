"""
pole_position_env.py

Implements a Gym environment for multi-car racing:
- Two cars: player_car & ai_car, or AI vs AI.
- Binaural audio: separate left/right channels based on each car's speed or position.
"""

import numpy as np
import gymnasium as gym
try:
    import pygame  # optional dependency for graphics
except Exception:  # pragma: no cover - optional dependency may be missing
    pygame = None
try:
    import simpleaudio as sa
except Exception:  # pragma: no cover - optional dependency
    sa = None

from ..physics.car import Car
from ..physics.track import Track
from ..physics.traffic_car import TrafficCar
from ..agents.controllers import GPTPlanner, LowLevelController, LearningAgent

class PolePositionEnv(gym.Env):
    """
    A multi-car racing environment with:
    - Toroidal 2D track
    - Binaural audio based on each car's speed
    - GPT-based high-level plan for Car B
    - A single discrete action for Car A (player or random)
    """

    metadata = {"render_modes": ["human"], "render_fps": 30}

    def __init__(self, render_mode="human", mode: str = "race", track_name: str | None = None):
        super().__init__()
        self.render_mode = render_mode
        self.mode = mode

        # Track & cars
        self.track = Track.load(track_name) if track_name else Track(width=200.0, height=200.0)
        self.cars = [Car(x=50, y=50), Car(x=150, y=150)]
        self.traffic: list[TrafficCar] = []
        if self.mode == "race":
            for i in range(20):
                x = (i * 10) % self.track.width
                self.traffic.append(TrafficCar(x=x, y=self.track.height / 2))
        
        # AI components for second car
        self.planner = GPTPlanner()         # High-level
        self.low_level = LowLevelController()
        self.learning_agent = LearningAgent()

        # Action space for Car 0 when controlled by a human or AI.
        # throttle: {0,1}, brake: {0,1}, steer: [-1,1]
        self.action_space = gym.spaces.Dict({
            "throttle": gym.spaces.Discrete(2),
            "brake": gym.spaces.Discrete(2),
            "steer": gym.spaces.Box(low=-1.0, high=1.0, shape=())
        })

        # Observations: (car0_x, car0_y, car0_speed, car1_x, car1_y, car1_speed, remaining_time)
        high = np.array([
            self.track.width,
            self.track.height,
            self.cars[0].max_speed,
            self.track.width,
            self.track.height,
            self.cars[1].max_speed,
            999.0,
        ] + [self.track.width, self.track.height] * 5, dtype=np.float32)
        low = np.array([0.0] * (7 + 10), dtype=np.float32)
        self.k_traffic = 5
        self.observation_space = gym.spaces.Box(low, high, shape=(7 + 10,), dtype=np.float32)
        self.remaining_time = 0.0
        self.next_checkpoint = 0.25
        self.qualifying_time = None
        self.passes = 0
        self.crashes = 0
        self.crash_timer = 0.0
        self.safe_point = (50.0, 50.0)

        self.audio_stream = None
        self.current_step = 0
        self.max_steps = 500  # limit episode length

        # pygame-related attributes (initialized lazily)
        self.screen = None
        self.clock = None
        self._scale = 3  # pixels per track unit

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.current_step = 0
        self.remaining_time = 90.0 if self.mode == "qualify" else 75.0
        self.next_checkpoint = 0.25
        self.qualifying_time = None
        self.crash_timer = 0.0

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
        self.current_step += 1
        self.remaining_time = max(self.remaining_time - 1.0, 0.0)
        prev_obs = self._get_obs()
        reward = 0.0

        # ---- Car 0 (Player / Random) ----
        throttle, brake, steer, gear_cmd = False, False, 0.0, 0
        if isinstance(action, (tuple, list)):
            if len(action) >= 3:
                throttle, brake, steer = bool(action[0]), bool(action[1]), float(action[2])
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
        self.cars[0].apply_controls(throttle, brake, steer, dt=1.0)

        if self.mode == "race":
            # ---- Car 1 (AI) ----
            state_dict = {
                "x": self.cars[1].x,
                "y": self.cars[1].y,
                "speed": self.cars[1].speed,
            }
            plan_text = self.planner.generate_plan(state_dict)

            tokens = plan_text.strip().split()
            try:
                target_speed = float(tokens[-1])
            except ValueError:
                target_speed = self.cars[1].speed

            dx = self.cars[0].x - self.cars[1].x
            dy = self.cars[0].y - self.cars[1].y
            dx = (dx + self.track.width / 2) % self.track.width - self.track.width / 2
            dy = (dy + self.track.height / 2) % self.track.height - self.track.height / 2
            target_angle = np.arctan2(dy, dx)
            heading_error = ((target_angle - self.cars[1].angle + np.pi) % (2 * np.pi)) - np.pi

            throttle_ai, brake_ai, steer_ai = self.low_level.compute_controls(
                self.cars[1].speed,
                target_speed,
                heading_error=heading_error,
            )
            self.cars[1].apply_controls(throttle_ai, brake_ai, steer_ai, dt=1.0)

            for t in self.traffic:
                th, br = t.policy()
                t.apply_controls(th, br, 0.0, dt=1.0)
                self.track.wrap_position(t)

        # Wrap positions on the track
        for c in self.cars:
            self.track.wrap_position(c)

        if self.crash_timer > 0:
            self.crash_timer -= 1.0
            if self.crash_timer <= 0:
                self.cars[0].x, self.cars[0].y = self.safe_point
                self.cars[0].speed = 0.0
        else:
            self.safe_point = (self.cars[0].x, self.cars[0].y)
            for t in self.traffic:
                if abs(t.x - self.cars[0].x) < Car.length and abs(t.y - self.cars[0].y) < Car.width / 2:
                    self.crashes += 1
                    self.crash_timer = 2.5
                    reward = -10.0
                    return self._get_obs(), reward, False, False, {}

        # Binaural audio: generate waveform based on each car's speed
        self._play_binaural_audio()

        progress = self.track.progress(self.cars[0])
        done = False
        if self.mode == "qualify":
            elapsed = (90.0 - self.remaining_time)
            reward = progress - 0.1 * elapsed
            if progress >= 1.0:
                self.qualifying_time = elapsed
                done = True
        else:  # race
            reward = self.cars[0].speed * 0.05
            while progress >= self.next_checkpoint:
                self.remaining_time += 30.0
                self.next_checkpoint += 0.25

        if self.mode == "race":
            dist = self.track.distance(self.cars[0], self.cars[1])
            if dist < 5.0:
                reward -= 1.0

        done = done or self.remaining_time <= 0 or (self.current_step >= self.max_steps)

        experience = (prev_obs, action, reward, self._get_obs())
        self.learning_agent.update_on_experience([experience])

        return self._get_obs(), reward, done, False, {}

    def render(self):
        """Render the environment."""
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
            pygame.init()
            size = (int(self.track.width * self._scale), int(self.track.height * self._scale))
            self.screen = pygame.display.set_mode(size)
            pygame.display.set_caption("Super Pole Position")
            self.clock = pygame.time.Clock()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close()
                return

        self.screen.fill((0, 0, 0))
        # Track border
        pygame.draw.rect(
            self.screen,
            (50, 50, 50),
            pygame.Rect(0, 0, self.track.width * self._scale, self.track.height * self._scale),
            2,
        )

        colors = [(255, 0, 0), (0, 255, 0)]
        for car, color in zip(self.cars, colors):
            x = int(car.x * self._scale)
            y = int(car.y * self._scale)
            pygame.draw.circle(self.screen, color, (x, y), 5)

        pygame.display.flip()
        if self.clock:
            self.clock.tick(self.metadata.get("render_fps", 30))

    def _play_binaural_audio(self, duration=0.5, sample_rate=44100):
        """
        Each step, generate separate sine waves (left for Car0, right for Car1).
        """
        if sa is None:
            return

        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        # Frequencies
        freq_left = 10.0 * self.cars[0].speed  # scale speed => audible freq
        freq_right = 10.0 * self.cars[1].speed

        # Sine wave for each channel
        left_wave = 0.3 * np.sin(2 * np.pi * freq_left * t)
        right_wave = 0.3 * np.sin(2 * np.pi * freq_right * t)

        # Interleave channels
        waveform = np.vstack((left_wave, right_wave)).T
        # Convert to 16-bit PCM for simpleaudio
        waveform_int16 = np.int16(waveform * 32767)

        # Stop previous sound if playing
        if self.audio_stream is not None:
            self.audio_stream.stop()

        self.audio_stream = sa.play_buffer(
            waveform_int16,
            num_channels=2,
            bytes_per_sample=2,
            sample_rate=sample_rate
        )

    def close(self):
        """Clean up resources like audio streams."""
        if self.audio_stream is not None:
            try:
                self.audio_stream.stop()
            except Exception:
                pass
            self.audio_stream = None

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
            ordered = [t for _, t in sorted(zip(dists, self.traffic), key=lambda p: p[0])]
            for t in ordered[: self.k_traffic]:
                dx = (t.x - self.cars[0].x)
                dy = (t.y - self.cars[0].y)
                traffic_rel.extend([dx, dy])
        while len(traffic_rel) < 2 * self.k_traffic:
            traffic_rel.extend([0.0, 0.0])
        return np.array(base + traffic_rel, dtype=np.float32)
