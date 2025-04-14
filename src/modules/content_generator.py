from typing import Dict, Any
from langchain_openai import ChatOpenAI
from src.utils.config import OPENAI_API_KEY


class ContentGenerator:
    """Generates posts and comments using LLM."""

    def __init__(self):
        """Initialize the generator with OpenAI client."""
        self.llm = ChatOpenAI(
            openai_api_key=OPENAI_API_KEY,
            model="gpt-4",
            temperature=0.7,
            max_tokens=500
        )

    def generate_post(self, profile: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Generate a post based on profile and context."""
        style = profile.get("style", "informal")
        interests = ", ".join(profile.get("interests", []))
        prompt = (
            f"Write a {style} social media post for a user interested in {interests}. "
            f"Context: {context.get('trends', [])}. Keep it concise and engaging."
        )
        return self.llm.invoke(prompt).content

    def generate_comment(self, post: Dict[str, Any], profile: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Generate a comment for a post."""
        style = profile.get("style", "informal")
        prompt = (
            f"Write a {style} comment for the post: {post.get('text', '')}. "
            f"Context: {context.get('analysis', '')}. Keep it relevant and natural."
        )
        return self.llm.invoke(prompt).content