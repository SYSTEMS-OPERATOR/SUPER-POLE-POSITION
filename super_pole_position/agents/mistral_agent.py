#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 MIND INTERFACES, INC. All rights reserved.
# Licensed under the MIT License.

"""
mistral_agent.py
Description: Module for Super Pole Position.
"""


from __future__ import annotations

import json
import os
from typing import Any, TYPE_CHECKING

from .base_llm_agent import BaseLLMAgent, NullAgent

try:
    from mistralai.client import MistralClient
except Exception:  # pragma: no cover - optional dependency
    MistralClient = None

if TYPE_CHECKING:  # pragma: no cover - type hints only
    from mistralai.client import MistralClient as _MistralClient  # noqa: F401


class MistralAgent(BaseLLMAgent):
    """Agent that uses mistralai SDK."""

    def __init__(self, model: str = "mistral-large-2402") -> None:
        """Set up the SDK client if the environment allows network access."""

        self.model = model
        self._enabled = MistralClient is not None and os.getenv("ALLOW_NET") == "1"
        self.client = (
            MistralClient(os.getenv("MISTRAL_API_KEY")) if self._enabled else None
        )

    def act(self, observation: Any) -> dict[str, float | int]:
        """Query the model and return an action dict."""

        if not self._enabled or self.client is None:
            return NullAgent().act(observation)
        prompt = f"Observation: {observation}. Return JSON with throttle, brake, steer."
        try:
            resp = self.client.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
            )
            content = resp.choices[0].message.content
            data = json.loads(content)
            return {
                "throttle": int(data.get("throttle", 0)),
                "brake": int(data.get("brake", 0)),
                "steer": float(data.get("steer", 0.0)),
            }
        except Exception as exc:  # pragma: no cover - network failure
            print(f"MistralAgent error: {exc}", flush=True)
            return NullAgent().act(observation)
