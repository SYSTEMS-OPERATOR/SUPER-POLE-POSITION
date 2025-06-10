from __future__ import annotations

import json
import os
from typing import Any

from .base_llm_agent import BaseLLMAgent, NullAgent

try:
    from mistralai.client import MistralClient  # type: ignore
except Exception:  # pragma: no cover
    MistralClient = None


class MistralAgent(BaseLLMAgent):
    """Agent that uses mistralai SDK."""

    def __init__(self, model: str = "mistral-large-2402") -> None:
        self.model = model
        self._enabled = MistralClient is not None and os.getenv("ALLOW_NET") == "1"
        self.client = MistralClient(os.getenv("MISTRAL_API_KEY")) if self._enabled else None

    def act(self, observation: Any) -> dict:
        if not self._enabled or self.client is None:
            return NullAgent().act(observation)
        prompt = f"Observation: {observation}. Return JSON with throttle, brake, steer."
        resp = self.client.chat(model=self.model, messages=[{"role": "user", "content": prompt}])
        content = resp.choices[0].message.content
        try:
            data = json.loads(content)
            return {"throttle": int(data.get("throttle", 0)), "brake": int(data.get("brake", 0)), "steer": float(data.get("steer", 0.0))}
        except Exception:
            return NullAgent().act(observation)
