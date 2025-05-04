from dataclasses import dataclass
from typing import List


@dataclass
class UserProfile:
    interests: List[str]
    style: str
    nick: str