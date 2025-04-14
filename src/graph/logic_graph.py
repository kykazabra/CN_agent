from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel
from typing import Dict, Any
from src.models.user_profile import UserProfile
from mastodon import Mastodon
import random


# Структура для анализа тональности
class SentimentAnalysis(BaseModel):
    sentiment: str  # "positive", "neutral", "negative"
    relevance: float  # 0.0–1.0


# Состояние графа
class AgentState(Dict[str, Any]):
    profile: UserProfile
    context: Dict[str, Any]
    action: str
    content: str


def build_graph(profile: UserProfile, mastodon: Mastodon, llm_config: Dict) -> StateGraph:
    """Создает граф логики для управления поведением агента."""
    llm = ChatOpenAI(
        model=llm_config['model'],
        temperature=llm_config['temperature'],
        max_tokens=llm_config['max_tokens']
    )

    graph = StateGraph(AgentState)

    # Узел анализа контекста
    def analyze_context(state: AgentState) -> AgentState:
        context = state.get('context', {})
        if not context:
            state['context'] = {'sentiment': 'neutral', 'relevance': 0.5}
            return state

        prompt = ChatPromptTemplate.from_template(
            "Проанализируй текст поста: {text}\n"
            "Определи тональность (позитивная, нейтральная, негативная) и релевантность для интересов: {interests}"
        )
        chain = prompt | llm.with_structured_output(SentimentAnalysis)
        result = chain.invoke({
            'text': context.get('text', ''),
            'interests': ', '.join(profile.interests)
        })
        state['context'] = {
            'sentiment': result.sentiment,
            'relevance': result.relevance,
            'text': context.get('text', '')
        }
        return state

    # Узел принятия решений
    def decide_action(state: AgentState) -> AgentState:
        relevance = state['context'].get('relevance', 0.5)
        sentiment = state['context'].get('sentiment', 'neutral')

        # Вероятности действий
        actions = {
            'post': profile.post_frequency / 24,  # Частота в час
            'comment': relevance * 0.3 if sentiment != 'negative' else 0.1,
            'like': relevance * 0.5,
            'reply': 0.8 if state['context'].get('is_mention', False) else 0.0
        }
        state['action'] = random.choices(
            list(actions.keys()),
            weights=list(actions.values()),
            k=1
        )[0]
        return state

    # Узел генерации контента
    def generate_content(state: AgentState) -> AgentState:
        action = state['action']
        prompt_map = {
            'post': (
                "Напиши пост в стиле {style} на тему, связанную с интересами: {interests}"
            ),
            'comment': (
                "Напиши комментарий в стиле {style} к посту: {text}"
            ),
            'reply': (
                "Ответь на упоминание в стиле {style}: {text}"
            )
        }

        if action in prompt_map:
            prompt = ChatPromptTemplate.from_template(prompt_map[action])
            chain = prompt | llm
            content = chain.invoke({
                'style': profile.style,
                'interests': ', '.join(profile.interests),
                'text': state['context'].get('text', '')
            }).content
            state['content'] = content
        else:
            state['content'] = None
        return state

    # Узел взаимодействия
    def interact(state: AgentState) -> AgentState:
        action = state['action']
        content = state['content']
        if action == 'post' and content:
            mastodon.status_post(content)
        elif action == 'comment' and content:
            post_id = state['context'].get('post_id')
            if post_id:
                mastodon.status_post(content, in_reply_to_id=post_id)
        elif action == 'reply' and content:
            mention_id = state['context'].get('mention_id')
            if mention_id:
                mastodon.status_post(content, in_reply_to_id=mention_id)
        elif action == 'like':
            post_id = state['context'].get('post_id')
            if post_id:
                mastodon.status_favourite(post_id)
        return state

    # Определение узлов
    graph.add_node("analyze_context", analyze_context)
    graph.add_node("decide_action", decide_action)
    graph.add_node("generate_content", generate_content)
    graph.add_node("interact", interact)

    # Определение ребер
    graph.set_entry_point("analyze_context")
    graph.add_edge("analyze_context", "decide_action")
    graph.add_edge("decide_action", "generate_content")
    graph.add_conditional_edges(
        "generate_content",
        lambda state: "interact" if state['content'] or state['action'] == 'like' else END
    )
    graph.add_edge("interact", END)

    return graph.compile()