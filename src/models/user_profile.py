from dataclasses import dataclass
from typing import List


@dataclass
class UserProfile:
    interests: List[str]
    post_frequency: float
    style: str
    nick: str
    post_time: List[int]