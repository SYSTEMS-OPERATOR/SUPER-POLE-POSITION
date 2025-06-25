import pytest

from super_pole_position.envs.pole_position import PolePositionEnv
from super_pole_position.agents.openai_agent import OpenAIAgent
from super_pole_position.agents.mistral_agent import MistralAgent


def _run_agent(agent_cls):
    env = PolePositionEnv(render_mode="human", mode="race")
    env.reset()
    agent = agent_cls()
    for _ in range(10):
        obs = env._get_obs()
        action = agent.act(obs)
        env.step(action)
    env.close()


def test_openai_agent_fallback(monkeypatch):
    monkeypatch.delenv("ALLOW_NET", raising=False)
    _run_agent(OpenAIAgent)


def test_mistral_agent_fallback(monkeypatch):
    monkeypatch.delenv("ALLOW_NET", raising=False)
    _run_agent(MistralAgent)
