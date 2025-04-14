from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from src.utils.config import OPENAI_API_KEY


class ContextAnalyzer:
    """Analyzes the social network context."""

    def __init__(self):
        """Initialize the analyzer with OpenAI client."""
        self.llm = ChatOpenAI(
            openai_api_key=OPENAI_API_KEY,
            model="gpt-4",
            temperature=0.7,
            max_tokens=200
        )

    def analyze_posts(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze a list of posts for relevance and engagement."""
        context = {"relevant_posts": [], "trends": []}
        for post in posts:
            prompt = f"Analyze the post: {post['text']}. Determine its topic, sentiment, and relevance for a tech enthusiast."
            response = self.llm.invoke(prompt).content
            context["relevant_posts"].append({
                "text": post["text"],
                "likes": post.get("likes", 0),
                "analysis": response
            })
        context["trends"] = ["#AI"]  # Simplified trend detection
        return context

    def detect_trends(self) -> List[str]:
        """Detect trending topics or hashtags."""
        return ["#AI", "#Tech"]

    def analyze_comment(self, comment: str) -> Dict[str, Any]:
        """Analyze a comment's sentiment and context."""
        prompt = f"Analyze the comment: {comment}. Determine its sentiment and intent."
        response = self.llm.invoke(prompt).content
        return {"comment": comment, "analysis": response}