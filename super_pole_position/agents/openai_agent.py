from __future__ import annotations

import json
import os
from typing import Any

from .base_llm_agent import BaseLLMAgent, NullAgent

try:
    import openai  # type: ignore
except Exception:  # pragma: no cover
    openai = None


class OpenAIAgent(BaseLLMAgent):
    """Agent that delegates decision-making to OpenAI API."""

    def __init__(self, model: str = "gpt-3.5-turbo") -> None:
        self.model = model
        self._enabled = openai is not None and os.getenv("ALLOW_NET") == "1"

    def act(self, observation: Any) -> dict:
        if not self._enabled:
            return NullAgent().act(observation)
        prompt = f"Observation: {observation}. Return JSON with throttle, brake, steer."
        resp = openai.chat.completions.create(model=self.model, messages=[{"role": "user", "content": prompt}])
        content = resp.choices[0].message.content
        try:
            data = json.loads(content)
            return {"throttle": int(data.get("throttle", 0)), "brake": int(data.get("brake", 0)), "steer": float(data.get("steer", 0.0))}
        except Exception:
            return NullAgent().act(observation)
