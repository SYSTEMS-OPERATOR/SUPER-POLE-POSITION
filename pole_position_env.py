"""
pole_position_env.py

Implements a Gym environment for multi-car racing:
- Two cars: player_car & ai_car, or AI vs AI.
- Binaural audio: separate left/right channels based on each car's speed or position.
"""

import numpy as np
import gym
try:
    import simpleaudio as sa
except Exception:  # pragma: no cover - optional dependency
    sa = None

from car import Car
from track import Track
from ai_controllers import GPTPlanner, LowLevelController, LearningAgent

class PolePositionEnv(gym.Env):
    """
    A multi-car racing environment with:
    - Toroidal 2D track
    - Binaural audio based on each car's speed
    - GPT-based high-level plan for Car B
    - A single discrete action for Car A (player or random)
    """

    metadata = {"render_modes": ["human"], "render_fps": 30}

    def __init__(self, render_mode="human"):
        super().__init__()
        self.render_mode = render_mode

        # Track & cars
        self.track = Track(width=200.0, height=200.0)
        self.cars = [Car(x=50, y=50), Car(x=150, y=150)]
        
        # AI components for second car
        self.planner = GPTPlanner()         # High-level
        self.low_level = LowLevelController()
        self.learning_agent = LearningAgent()

        # For multi-agent or expansions, define an action_space for each agent.
        # Here, we define a single Discrete(3) for Car 0 (player) => throttle, brake, no-op.
        self.action_space = gym.spaces.Discrete(3)

        # Observations: (car0_x, car0_y, car0_speed, car1_x, car1_y, car1_speed)
        high = np.array([self.track.width, self.track.height,  self.cars[0].max_speed,
                         self.track.width, self.track.height,  self.cars[1].max_speed],
                        dtype=np.float32)
        low = np.array([0.0, 0.0, 0.0,  0.0, 0.0,  0.0], dtype=np.float32)
        self.observation_space = gym.spaces.Box(low, high, shape=(6,), dtype=np.float32)

        self.audio_stream = None
        self.current_step = 0
        self.max_steps = 500  # limit episode length

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.current_step = 0

        # Reset cars to start positions
        self.cars[0].x = 50.0
        self.cars[0].y = 50.0
        self.cars[0].angle = 0.0
        self.cars[0].speed = 0.0

        self.cars[1].x = 150.0
        self.cars[1].y = 150.0
        self.cars[1].angle = 0.0
        self.cars[1].speed = 0.0

        # Return initial observation
        return self._get_obs(), {}

    def step(self, action):
        """
        Single action for Car 0 => 0=throttle, 1=brake, 2=no-action
        Car 1 is AI-driven using GPT plan + LowLevelController
        """
        self.current_step += 1
        prev_obs = self._get_obs()

        # ---- Car 0 (Player / Random) ----
        throttle, brake, steer = False, False, 0.0
        if action == 0:
            throttle = True
        elif action == 1:
            brake = True
        # else action==2 => no action

        self.cars[0].apply_controls(throttle, brake, steer, dt=1.0)

        # ---- Car 1 (AI) ----
        # High-level plan from GPT
        state_dict = {
            "x": self.cars[1].x,
            "y": self.cars[1].y,
            "speed": self.cars[1].speed
        }
        plan_text = self.planner.generate_plan(state_dict)

        # Example: parse last token as a target speed
        tokens = plan_text.strip().split()
        try:
            target_speed = float(tokens[-1])
        except ValueError:
            target_speed = self.cars[1].speed  # fallback to current

        # Steering towards Car 0
        dx = self.cars[0].x - self.cars[1].x
        dy = self.cars[0].y - self.cars[1].y
        dx = (dx + self.track.width / 2) % self.track.width - self.track.width / 2
        dy = (dy + self.track.height / 2) % self.track.height - self.track.height / 2
        target_angle = np.arctan2(dy, dx)
        heading_error = ((target_angle - self.cars[1].angle + np.pi) % (2 * np.pi)) - np.pi

        (throttle_ai, brake_ai, steer_ai) = self.low_level.compute_controls(
            self.cars[1].speed,
            target_speed,
            heading_error=heading_error
        )
        self.cars[1].apply_controls(throttle_ai, brake_ai, steer_ai, dt=1.0)

        # Wrap positions on the track
        for c in self.cars:
            self.track.wrap_position(c)

        # Binaural audio: generate waveform based on each car's speed
        self._play_binaural_audio()

        # Reward: e.g. Car 0 gets reward for going faster or for time alive
        reward = self.cars[0].speed * 0.05

        # Optionally, check collisions or add penalty
        dist = self.track.distance(self.cars[0], self.cars[1])
        if dist < 5.0:
            # E.g. collision penalty or partial slowdown
            reward -= 1.0

        # Done if max steps reached
        done = (self.current_step >= self.max_steps)

        # Example "real-time learning" for Car 1: gather experience
        experience = (prev_obs, action, reward, self._get_obs())
        self.learning_agent.update_on_experience([experience])

        return self._get_obs(), reward, done, False, {}

    def render(self):
        """
        Minimal textual render in console.
        For real usage, integrate pygame or another library for visuals.
        """
        if self.render_mode == "human":
            print(f"Car0: ({self.cars[0].x:.2f}, {self.cars[0].y:.2f}) "
                  f"Spd={self.cars[0].speed:.2f} | "
                  f"Car1: ({self.cars[1].x:.2f}, {self.cars[1].y:.2f}) "
                  f"Spd={self.cars[1].speed:.2f}")

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

    def _get_obs(self):
        """
        Observation: [car0_x, car0_y, car0_speed, car1_x, car1_y, car1_speed]
        """
        return np.array([
            self.cars[0].x,
            self.cars[0].y,
            self.cars[0].speed,
            self.cars[1].x,
            self.cars[1].y,
            self.cars[1].speed
        ], dtype=np.float32)
