from typing import Dict, Any
from src.graph.logic_graph import LogicGraph
from src.agents.profile_manager import ProfileManager


class LLMAgent:
    """LLM Agent for simulating human activity in a social network."""

    def __init__(self, profile_path: str):
        """Initialize the agent with a user profile."""
        self.profile_manager = ProfileManager(profile_path)
        self.profile = self.profile_manager.load_profile()
        self.graph = LogicGraph(self.profile)

    def run(self, max_iterations: int = 10) -> None:
        """Run the agent's logic graph for a specified number of iterations."""
        state = {"context": {}, "action_history": []}
        for _ in range(max_iterations):
            state = self.graph.run(state)
            if state.get("action") == "end":
                break

    def execute_action(self, action: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific action based on the graph's decision."""
        return self.graph.execute_action(action, context)