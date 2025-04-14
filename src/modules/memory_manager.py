import json
import os
from typing import Dict, Any, List
from datetime import datetime


class MemoryManager:
    """Manages the agent's action history."""

    def __init__(self, storage_path: str = "data/memory/memory.json"):
        """Initialize with storage path."""
        self.storage_path = storage_path
        os.makedirs(os.path.dirname(storage_path), exist_ok=True)
        if not os.path.exists(storage_path):
            with open(storage_path, 'w', encoding='utf-8') as f:
                json.dump([], f)

    def save_action(self, action_type: str, details: Dict[str, Any]) -> None:
        """Save an action to memory."""
        details["timestamp"] = datetime.now().isoformat()
        details["type"] = action_type
        with open(self.storage_path, 'r', encoding='utf-8') as f:
            history = json.load(f)
        history.append(details)
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)

    def get_history(self) -> List[Dict[str, Any]]:
        """Retrieve the action history."""
        with open(self.storage_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def check_action(self, action_type: str, details: Dict[str, Any]) -> bool:
        """Check if an action has been performed before."""
        history = self.get_history()
        for action in history:
            if action["type"] == action_type and action.get("content") == details.get("content"):
                return True
        return False