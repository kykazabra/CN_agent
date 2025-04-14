from mastodon import StreamListener
from src.models.user_profile import UserProfile
from mastodon import Mastodon
from typing import Any


class BotStreamListener(StreamListener):
    def __init__(self, graph: Any, profile: UserProfile, mastodon: Mastodon):
        super().__init__()
        self.graph = graph
        self.profile = profile
        self.mastodon = mastodon

    def on_update(self, status: dict):
        """Обрабатывает новые посты в ленте."""
        text = status['content']
        post_id = status['id']
        state = {
            'profile': self.profile,
            'context': {
                'text': text,
                'post_id': post_id,
                'is_mention': False
            }
        }
        self.graph.invoke(state)

    def on_notification(self, notification: dict):
        """Обрабатывает упоминания бота."""
        if notification['type'] == 'mention':
            text = notification['status']['content']
            mention_id = notification['status']['id']
            state = {
                'profile': self.profile,
                'context': {
                    'text': text,
                    'mention_id': mention_id,
                    'is_mention': True
                }
            }
            self.graph.invoke(state)