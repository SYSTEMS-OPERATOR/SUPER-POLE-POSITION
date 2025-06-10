"""
ai_controllers.py
 
Houses:
- GPTPlanner: High-level strategy using a GPT model.
- LowLevelController: Basic speed/steering control.
- LearningAgent: Placeholder for real-time learning / RL logic.
"""

try:
    import torch  # noqa: F401 - optional dependency
    from transformers import AutoTokenizer, AutoModelForCausalLM
except Exception:  # pragma: no cover - optional dependency may be missing
    torch = None
    AutoTokenizer = None
    AutoModelForCausalLM = None

class GPTPlanner:
    """High-level planner that can optionally use a GPT model."""

    def __init__(self, model_name: str = 'openai-community/gpt2') -> None:
        """Load the GPT model if the transformers stack is available."""
        if AutoTokenizer is None:
            # Dependencies missing – fall back to a deterministic planner.
            self.tokenizer = None
            self.model = None
        else:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(model_name)

    def generate_plan(self, state_dict):
        """Return a textual plan for the next action."""
        if self.tokenizer is None or self.model is None:
            # Fallback behaviour if transformers is unavailable
            return "target_speed 10"

        prompt = (
            "Car state:\n"
            f"- Speed: {state_dict['speed']}\n"
            f"- Position: ({state_dict['x']}, {state_dict['y']})\n"
            "Decide next action or speed target:\n"
        )
        inputs = self.tokenizer(prompt, return_tensors="pt")
        outputs = self.model.generate(**inputs, max_length=30, do_sample=False)
        plan_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return plan_text

class LowLevelController:
    """
    A simple controller that tries to match a target speed and minimal steering logic.
    This can be expanded or replaced by a proper RL or PID controller.
    """
    def compute_controls(self, current_speed, target_speed, heading_error=0.0):
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
    def __init__(self):
        # Simple experience buffer for demonstration purposes
        self.buffer = []

    def update_on_experience(self, experience_batch):
        """
        Stub method showing where you'd do gradient updates each step/lap.
        :param experience_batch: e.g. [(state, action, reward, next_state), ...]
        """
        # A real agent would perform gradient updates here.  We simply
        # accumulate the experiences so they can be inspected later.
        self.buffer.extend(experience_batch)
