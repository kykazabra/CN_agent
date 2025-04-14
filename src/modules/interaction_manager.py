from typing import Dict, Any
from src.modules.content_generator import ContentGenerator


class InteractionManager:
    """Manages interactions like comments, likes, and follows."""

    def __init__(self):
        """Initialize the interaction manager."""
        self.content_generator = ContentGenerator()

    def respond_to_comment(self, comment: str, profile: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Generate a response to a comment."""
        style = profile.get("style", "informal")
        prompt = (
            f"Write a {style} response to the comment: {comment}. "
            f"Context: {context.get('analysis', '')}. Keep it natural."
        )
        return self.content_generator.llm.invoke(prompt).content

    def like_post(self, post: Dict[str, Any], profile: Dict[str, Any]) -> bool:
        """Decide whether to like a post."""
        import random
        interests = profile.get("interests", [])
        post_text = post.get("text", "").lower()
        relevance = any(interest.lower() in post_text for interest in interests)
        return random.random() < (0.6 if relevance else 0.1)

    def follow_account(self, account: Dict[str, Any], profile: Dict[str, Any]) -> bool:
        """Decide whether to follow an account."""
        import random
        profile_interests = set(profile.get("interests", []))
        account_interests = set(account.get("interests", []))
        similarity = len(profile_interests.intersection(account_interests)) / len(
            profile_interests) if profile_interests else 0
        return random.random() < (0.4 if similarity > 0.5 else 0.1)