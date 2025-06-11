from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

class BaseLLMAgent(ABC):
    """Common interface for LLM-driven agents."""

    @abstractmethod
    def act(self, observation: Any) -> dict:
        """Return an action dict given an observation."""


class NullAgent(BaseLLMAgent):
    """Heuristic agent used for offline tests."""

    def act(self, observation: Any) -> dict:
        # Simple policy: throttle until half max speed, no steering
        speed = observation[2]
        throttle = speed < 5.0
        return {
            "throttle": int(throttle),
            "brake": int(not throttle),
            "steer": 0.0,
            "gear": 0,
        }
