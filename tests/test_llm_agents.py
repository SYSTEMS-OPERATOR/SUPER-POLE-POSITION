#!/usr/bin/env python3
"""Tests for LLM-backed agents fallbacks."""

from super_pole_position.agents.base_llm_agent import NullAgent
from super_pole_position.agents.openai_agent import OpenAIAgent
from super_pole_position.agents.mistral_agent import MistralAgent


OBS = [0, 0, 0]


def test_openai_agent_offline(monkeypatch):
    """OpenAI agent falls back to NullAgent when network disabled."""
    monkeypatch.delenv("ALLOW_NET", raising=False)
    agent = OpenAIAgent()
    assert agent.client is None
    assert agent.act(OBS) == NullAgent().act(OBS)


def test_mistral_agent_offline(monkeypatch):
    """Mistral agent falls back to NullAgent when network disabled."""
    monkeypatch.delenv("ALLOW_NET", raising=False)
    agent = MistralAgent()
    assert agent.client is None
    assert agent.act(OBS) == NullAgent().act(OBS)
