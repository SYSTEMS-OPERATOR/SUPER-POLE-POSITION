"""
main.py

Provides a simple training or demo loop to show usage of the PolePositionEnv.
"""

import argparse
try:
    import pygame  # optional for input
except Exception:  # pragma: no cover - optional dependency may be missing
    pygame = None

import gym
import numpy as np
from pole_position_env import PolePositionEnv

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--ai", action="store_true", help="Control Car 0 with AI instead of keyboard"
    )
    args = parser.parse_args()

    # Create environment
    env = PolePositionEnv(render_mode="human")

    human_control = not args.ai and pygame is not None

    num_episodes = 5
    for ep in range(num_episodes):
        obs, info = env.reset()
        done = False
        total_reward = 0.0
        steps = 0
        while not done:
            if human_control:
                pygame.event.pump()
                keys = pygame.key.get_pressed()
                throttle = keys[pygame.K_UP]
                brake = keys[pygame.K_DOWN]
                steer = 0.0
                if keys[pygame.K_LEFT]:
                    steer -= 0.5
                if keys[pygame.K_RIGHT]:
                    steer += 0.5
                action = (throttle, brake, steer)
            else:
                action = env.action_space.sample()

            obs, reward, done, trunc, info = env.step(action)
            total_reward += reward
            steps += 1

            env.render()

        print(f"Episode {ep+1} finished in {steps} steps with reward={total_reward:.2f}")

    env.close()

if __name__ == "__main__":
    main()
