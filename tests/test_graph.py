import pytest
from src.graph.logic_graph import LogicGraph


def test_graph_initialization():
    profile = {"id": "test", "interests": ["tech"], "post_frequency": 0.5}
    graph = LogicGraph(profile)
    assert graph.profile == profile


def test_graph_run():
    profile = {"id": "test", "interests": ["tech"], "post_frequency": 0.5}
    graph = LogicGraph(profile)
    state = {"context": {}, "action_history": []}
    result = graph.run(state)
    assert "action" in result