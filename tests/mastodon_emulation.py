from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class StatusPost:
    content: str
    in_reply_to_id: int = None


@dataclass
class StatusFavorite:
    post_id: int


@dataclass
class AccountFollow:
    user_id: str


@dataclass
class AccountUnfollow:
    user_id: str


class MastodonEmulator:
    def __init__(self):
        self.memory = []
        self.iteration_memory = []

    def step(self):
        self.memory.append(self.iteration_memory)
        self.iteration_memory = []

    def account_search(self, nick, *args, **kwargs) -> List:
        return [{'id': nick}]

    def status_post(self, content: str, in_reply_to_id: int = None) -> None:
        self.iteration_memory.append(StatusPost(content=content, in_reply_to_id=in_reply_to_id))

    def status_favourite(self, post_id: int) -> None:
        self.iteration_memory.append(StatusFavorite(post_id=post_id))

    def account_follow(self, user_id: str) ->  None:
        self.iteration_memory.append(AccountFollow(user_id=user_id))

    def account_unfollow(self, user_id: str) ->  None:
        self.iteration_memory.append(AccountUnfollow(user_id=user_id))


def typed_to_enum(inp: Dict) -> Any:
    return eval(f'{inp["type"]}(**{inp["args"]})')