from langchain.chains.question_answering.map_reduce_prompt import messages
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import Dict, Any, Literal, Union, Annotated, List
from typing_extensions import TypedDict
from src.models.user_profile import UserProfile
from mastodon import Mastodon
import random


# Структура для анализа тональности
class SentimentAnalysis(BaseModel):
    """Ananlysis about sentiment"""
    sentiment: Literal["positive", "neutral", "negative"]
    relevance: float  = Field(description='Could be number from 0 to 1')


class Decision(BaseModel):
    """Decision on what action to take"""
    action: Literal['post', 'reply', 'like', 'sub', 'unsub', 'pass'] = Field(description="""
post - написать новый пост у себя на странице
reply - ответить на сообщение
like - оценить сообщение
sub - подписаться на пользователя
unsub - отписаться от пользователя
pass - продолжить и ничего не делать
""")


# Состояние графа
class AgentState(TypedDict):
    profile: UserProfile
    context: Dict[str, Any]
    action: str
    content: str
    chat_history: List[Dict[str, str]]


def build_graph(profile: UserProfile, mastodon: Mastodon, checkpointer: Any, llm_config: Dict) -> StateGraph:
    """Создает граф логики для управления поведением агента."""
    llm = ChatOpenAI(**llm_config)

    graph = StateGraph(AgentState)


    def create_post(history: List) -> str:
        content = llm.invoke(history + [{'role': 'system', 'content': 'Ты решил написать пост, придумай текст для поста. В ответ выдавай только текст!'}]).content

        mastodon.status_post(content)

        return content


    def like_post(post_id: int) -> None:
        mastodon.status_favourite(post_id)

        return

    def reply_to_post(post_id: int, history: List) -> str:
        reply = llm.invoke(history + [{'role': 'system', 'content': 'Ты решил написать ответ пользователю'}]).content

        mastodon.status_post(reply, in_reply_to_id=post_id)

        return reply

    def sub_to_user(nick: str) -> None:
        results = mastodon.account_search(nick, limit=1)

        user_id = results[0]['id']
        mastodon.account_follow(user_id)

        return

    def unsub_from_user(nick: str) -> None:
        results = mastodon.account_search(nick, limit=1)

        user_id = results[0]['id']
        mastodon.account_unfollow(user_id)

        return

    def analyze_context(state: AgentState) -> AgentState:
        context = state.get('context', {})

        if not state.get('chat_history'):
            state['chat_history'] = [{
                'role': 'system',
                'content': f'Тебя зовут {profile.nick}, твои интересы: {profile.interests}, ты общаешься в стиле: {profile.style}'
            }]

        if state['context']['is_mention']:
            state['chat_history'].append({'role': 'user', 'content': f'Пользователь {context.get("user")} написал тебе сообщение: {context.get("text")}'})

        else:
            state['chat_history'].append({'role': 'user',
                                       'content': f'Пользователь {context.get("user")} написал пост: {context.get("text")}'})

        return state

    def decide_action(state: AgentState) -> AgentState:
        # Вероятности действий

        messages = state['chat_history'] + [{'role': 'system', 'content': 'Прими решение, что делать дальше'}]

        result = llm.with_structured_output(Decision).invoke(messages)

        state['action'] = result.action

        return state

    def make_action(state: AgentState) -> AgentState:
        action = state['action']

        if action == 'post':
            try:
                content = create_post(history=state['chat_history'])
                state['content'] = content
                state['chat_history'].append({'role': 'system', 'content': f'Ты написал пост у себя на странице: {content}'})

            except Exception as e:
                state['chat_history'].append({'role': 'system', 'content': f'У тебя не получилось написать пост у себя на странице по причине: {e}'})

        if action == 'reply':
            try:
                content = reply_to_post(post_id=state['context'].get('post_id'), history=state['chat_history'])
                state['content'] = content
                state['chat_history'].append({'role': 'system', 'content': f'Ты ответил пользователю: {content}'})

            except Exception as e:
                import traceback
                print(traceback.format_exc())
                state['chat_history'].append({'role': 'system',
                                           'content': f'У тебя не получилось ответить пользователю по причине: {e}'})

        if action == 'like':
            try:
                like_post(post_id=state['context'].get('post_id'))
                state['content'] = None
                state['chat_history'].append({'role': 'system', 'content': 'Ты поставил лайк последнему посту пользователя'})

            except Exception as e:
                state['chat_history'].append({'role': 'system',
                                           'content': f'У тебя не получилось поставить лайк последнему посту пользователя по причине: {e}'})

        if action == 'sub':
            try:
                sub_to_user(nick=state['context'].get('user'))
                state['content'] = None
                state['chat_history'].append({'role': 'system', 'content': 'Ты подписался на пользователя'})

            except Exception as e:
                state['chat_history'].append({'role': 'system',
                                           'content': f'У тебя не получилось подписаться на пользователяя по причине: {e}'})

        if action == 'unsub':
            try:
                unsub_from_user(nick=state['context'].get('user'))
                state['content'] = None
                state['chat_history'].append({'role': 'system', 'content': 'Ты отписался от пользователя'})

            except Exception as e:
                state['chat_history'].append({'role': 'system',
                                           'content': f'У тебя не получилось отписаться от пользователя по причине: {e}'})

        return state

    def route_by_status(state: AgentState) -> Literal["make_action", "end"]:
        if state['action'] != 'pass':
            return 'make_action'

        else:
            return "end"

    # Определение узлов
    graph.add_node("analyze_context", analyze_context)
    graph.add_node("decide_action", decide_action)
    graph.add_node("make_action", make_action)

    # Определение ребер
    graph.set_entry_point("analyze_context")
    graph.add_edge("analyze_context", "decide_action")
    graph.add_edge("make_action", "decide_action")

    graph.add_conditional_edges(
        "decide_action",
        route_by_status,
        {
            "make_action": "make_action",
            "end": END
        }
    )

    return graph.compile(checkpointer=checkpointer)