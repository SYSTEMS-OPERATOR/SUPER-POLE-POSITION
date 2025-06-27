#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 MIND INTERFACES, INC. All rights reserved.
# Licensed under the MIT License.

"""Controller helpers for Super Pole Position.

controllers.py
 
Houses:
- GPTPlanner: High-level strategy using a GPT model.
- LowLevelController: Basic speed/steering control.
- LearningAgent: Placeholder for real-time learning / RL logic.
"""

from typing import Any, Dict, Iterable, Tuple, cast

torch: Any | None = None
AutoTokenizer: Any | None = None
AutoModelForCausalLM: Any | None = None


def _import_llm_deps() -> None:
    """Attempt to import optional LLM dependencies lazily."""

    global torch, AutoTokenizer, AutoModelForCausalLM
    if AutoTokenizer is not None and AutoModelForCausalLM is not None:
        return
    try:  # pragma: no cover - optional dependency may be missing
        import importlib
        torch = importlib.import_module("torch")
        transformers = importlib.import_module("transformers")
        AutoTokenizer = getattr(transformers, "AutoTokenizer")
        AutoModelForCausalLM = getattr(transformers, "AutoModelForCausalLM")
    except Exception:
        torch = None
        AutoTokenizer = None
        AutoModelForCausalLM = None

class GPTPlanner:
    """High-level planner that can optionally use a GPT model."""

    def __init__(
        self,
        model_name: str = "openai-community/gpt2",
        autoload: bool = False,
    ) -> None:
        """Optionally set up the GPT model lazily."""

        self.model_name = model_name
        self.tokenizer: Any | None = None
        self.model: Any | None = None
        if autoload:
            self.load_model()

    def load_model(self) -> None:
        """Load the tokenizer and model when dependencies are available."""

        _import_llm_deps()
        if AutoTokenizer is None or AutoModelForCausalLM is None:
            return
        if self.tokenizer is None or self.model is None:
            assert AutoTokenizer is not None
            assert AutoModelForCausalLM is not None
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(self.model_name)

    def generate_plan(self, state_dict: Dict[str, Any]) -> str:
        """Return a textual plan for the next action."""
        if self.tokenizer is None or self.model is None:
            # Fallback behavior if transformers is unavailable
            return "target_speed 10"

        prompt = (
            "Car state:\n"
            f"- Speed: {state_dict['speed']}\n"
            f"- Position: ({state_dict['x']}, {state_dict['y']})\n"
            "Decide next action or speed target:\n"
        )
        inputs = self.tokenizer(prompt, return_tensors="pt")
        outputs = self.model.generate(**inputs, max_length=30, do_sample=False)
        plan_text = cast(str, self.tokenizer.decode(outputs[0], skip_special_tokens=True))
        return plan_text

class LowLevelController:
    """
    A simple controller that tries to match a target speed and minimal steering logic.
    This can be expanded or replaced by a proper RL or PID controller.
    """
    def compute_controls(
        self,
        current_speed: float,
        target_speed: float,
        heading_error: float = 0.0,
    ) -> Tuple[bool, bool, float]:
        """
        :param current_speed: The car's current speed.
        :param target_speed: Desired speed from the high-level planner.
        :param heading_error: Negative => need to turn left, positive => turn right.
        :return: (throttle: bool, brake: bool, steering: float)
        """
        throttle = current_speed < target_speed
        brake = current_speed > target_speed

        # Steering is a simple proportion for demonstration:
        steering = 0.0
        # e.g. if heading_error is positive, steer right
        # For now, we do minimal steering
        if abs(heading_error) > 0.01:
            steering = 0.1 if heading_error > 0 else -0.1

        return throttle, brake, steering

class LearningAgent:
    """
    Placeholder for real-time learning (RL) approach.
    In a real system, you'd manage experience buffers, do forward/backprop, etc.
    """
    def __init__(self) -> None:
        # Simple experience buffer for demonstration purposes
        self.buffer: list[Tuple[Any, Any, float, Any]] = []
        self.total_reward = 0.0
        self.avg_reward = 0.0

    def update_on_experience(
        self, experience_batch: Iterable[Tuple[Any, Any, float, Any]]
    ) -> None:
        """
        Stub method showing where you'd do gradient updates each step/lap.
        :param experience_batch: e.g. [(state, action, reward, next_state), ...]
        """
        # A real agent would perform gradient updates here.  We simply
        # accumulate the experiences so they can be inspected later.
        self.buffer.extend(experience_batch)

        # Track running reward statistics for basic learning diagnostics
        batch_reward = sum(exp[2] for exp in experience_batch)
        self.total_reward += batch_reward
        if self.buffer:
            self.avg_reward = self.total_reward / len(self.buffer)
