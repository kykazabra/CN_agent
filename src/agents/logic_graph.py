from typing import Dict, Any, Callable
from langgraph.graph import StateGraph
from src.modules.context_analyzer import ContextAnalyzer
from src.modules.content_generator import ContentGenerator
from src.modules.interaction_manager import InteractionManager
from src.modules.memory_manager import MemoryManager
import random
from datetime import datetime


class LogicGraph:
    """Implements the logic graph for the LLM agent."""

    def __init__(self, profile: Dict[str, Any]):
        """Initialize the graph with user profile."""
        self.profile = profile
        self.context_analyzer = ContextAnalyzer()
        self.content_generator = ContentGenerator()
        self.interaction_manager = InteractionManager()
        self.memory_manager = MemoryManager()
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the logic graph with nodes and edges."""
        graph = StateGraph()

        # Define nodes
        graph.add_node("initialize", self._initialize)
        graph.add_node("analyze_context", self._analyze_context)
        graph.add_node("decide", self._decide)
        graph.add_node("generate_content", self._generate_content)
        graph.add_node("interact", self._interact)
        graph.add_node("subscribe", self._subscribe)
        graph.add_node("update_memory", self._update_memory)
        graph.add_node("end", self._end)

        # Define edges
        graph.add_edge("initialize", "analyze_context")
        graph.add_conditional_edges(
            "analyze_context",
            self._context_to_decide,
            {"decide": "decide"}
        )
        graph.add_conditional_edges(
            "decide",
            self._decide_to_action,
            {
                "generate_content": "generate_content",
                "interact": "interact",
                "subscribe": "subscribe",
                "end": "end"
            }
        )
        graph.add_edge("generate_content", "update_memory")
        graph.add_edge("interact", "update_memory")
        graph.add_edge("subscribe", "update_memory")
        graph.add_conditional_edges(
            "update_memory",
            self._memory_to_next,
            {"analyze_context": "analyze_context", "end": "end"}
        )

        graph.set_entry_point("initialize")
        return graph.compile()

    def _initialize(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize the agent's state."""
        state["profile"] = self.profile
        state["context"] = {}
        state["action_history"] = []
        return state

    def _analyze_context(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the social network context."""
        posts = [{"text": "New AI tool released! #AI", "likes": 100}]
        state["context"] = self.context_analyzer.analyze_posts(posts)
        return state

    def _decide(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Decide on the next action based on probabilities."""
        hour = datetime.now().hour
        active_hours = self.profile.get("active_hours", [18, 22])
        post_prob = self.profile.get("post_frequency", 0.5) if hour in active_hours else 0.1
        comment_prob = 0.3 if state["context"].get("relevant_posts") else 0.1
        subscribe_prob = 0.1

        actions = ["generate_content", "interact", "subscribe", "end"]
        probs = [post_prob, comment_prob, subscribe_prob, 1 - sum([post_prob, comment_prob, subscribe_prob])]
        state["action"] = random.choices(actions, probs)[0]
        return state

    def _generate_content(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a post or comment."""
        content = self.content_generator.generate_post(self.profile, state["context"])
        state["last_action"] = {"type": "post", "content": content}
        return state

    def _interact(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Interact with a post or comment."""
        post = state["context"].get("relevant_posts", [{}])[0]
        comment = self.content_generator.generate_comment(post, self.profile, state["context"])
        state["last_action"] = {"type": "comment", "content": comment}
        return state

    def _subscribe(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Subscribe to an account."""
        account = {"id": "tech_account", "interests": ["tech"]}
        self.interaction_manager.follow_account(account, self.profile)
        state["last_action"] = {"type": "subscribe", "account": account["id"]}
        return state

    def _update_memory(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Update memory with the last action."""
        if "last_action" in state:
            self.memory_manager.save_action(state["last_action"]["type"], state["last_action"])
            state["action_history"].append(state["last_action"])
        return state

    def _end(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """End the iteration."""
        state["action"] = "end"
        return state

    def _context_to_decide(self, state: Dict[str, Any]) -> str:
        """Transition from context analysis to decision."""
        return "decide"

    def _decide_to_action(self, state: Dict[str, Any]) -> str:
        """Transition from decision to action."""
        return state["action"]

    def _memory_to_next(self, state: Dict[str, Any]) -> str:
        """Transition from memory update to next step."""
        return "analyze_context" if len(state["action_history"]) < 10 else "end"

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Run the graph with the current state."""
        return self.graph.invoke(state)

    def execute_action(self, action: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific action."""
        state = {"context": context, "action": action, "profile": self.profile}
        if action == "generate_content":
            return self._generate_content(state)
        elif action == "interact":
            return self._interact(state)
        elif action == "subscribe":
            return self._subscribe(state)
        return state