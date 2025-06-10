"""
main.py

Provides a simple training or demo loop to show usage of the PolePositionEnv.
"""

import gym
import numpy as np
from pole_position_env import PolePositionEnv

def main():
    # Create environment
    env = PolePositionEnv(render_mode="human")

    num_episodes = 5
    for ep in range(num_episodes):
        obs, info = env.reset()
        done = False
        total_reward = 0.0
        steps = 0
        while not done:
            # For demonstration: random action for Car 0
            action = env.action_space.sample()

            # Step environment
            obs, reward, done, trunc, info = env.step(action)
            total_reward += reward
            steps += 1

            env.render()

        print(f"Episode {ep+1} finished in {steps} steps with reward={total_reward:.2f}")

    # Print summary for the final episode and clean up
    env._summarize_episode()
    env.close()

if __name__ == "__main__":
    main()
