import pytest
from src.agents.llm_agent import LLMAgent


def test_agent_initialization():
    agent = LLMAgent("data/profiles/user_tech.json")
    assert agent.profile["id"] == "user_tech"


def test_agent_run():
    agent = LLMAgent("data/profiles/user_tech.json")
    agent.run(max_iterations=1)  # Should not raise exceptions