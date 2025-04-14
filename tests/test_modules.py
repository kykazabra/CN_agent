import pytest
from src.modules.content_generator import ContentGenerator
from src.modules.context_analyzer import ContextAnalyzer


def test_content_generator():
    generator = ContentGenerator()
    profile = {"interests": ["tech"], "style": "informal"}
    content = generator.generate_post(profile, {})
    assert isinstance(content, str)
    assert len(content) > 0


def test_context_analyzer():
    analyzer = ContextAnalyzer()
    posts = [{"text": "Test post #AI", "likes": 10}]
    context = analyzer.analyze_posts(posts)
    assert "relevant_posts" in context
    assert len(context["relevant_posts"]) == 1