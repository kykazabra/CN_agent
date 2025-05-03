from mastodon import StreamListener
from sqlalchemy.testing.plugin.plugin_base import config

from src.models.user_profile import UserProfile
from mastodon import Mastodon
from typing import Any
from bs4 import BeautifulSoup


class BotStreamListener(StreamListener):
    def __init__(self, graph: Any, profile: UserProfile, mastodon: Mastodon):
        super().__init__()
        self.graph = graph
        self.profile = profile
        self.mastodon = mastodon

    # def on_update(self, status: dict):
    #     """Обрабатывает новые посты в ленте."""
    #
    #     user =  status['account']['username']
    #
    #     if user != self.profile.nick:
    #         text = BeautifulSoup(status['content'], "html.parser").get_text()
    #         post_id = status['id']
    #
    #         state = {
    #             'profile': self.profile,
    #             'context': {
    #                 'text': text,
    #                 'post_id': post_id,
    #                 'is_mention': False,
    #                 'user': user
    #             }
    #         }
    #
    #         config = {"configurable": {"thread_id": user}, "recursion_limit": 8}
    #
    #         self.graph.invoke(state, config=config)

    def on_notification(self, notification: dict):
        """Обрабатывает упоминания бота."""
        user =  notification['account']['username']

        if notification['type'] == 'mention':
            text =  BeautifulSoup(notification['status']['content'], "html.parser").get_text()
            mention_id = notification['status']['id']

            state = {
                'profile': self.profile,
                'context': {
                    'text': text,
                    'post_id': mention_id,
                    'is_mention': True,
                    'user': user,
                }
            }

            config = {"configurable": {"thread_id": user}, "recursion_limit": 8}

            self.graph.invoke(state, config=config)