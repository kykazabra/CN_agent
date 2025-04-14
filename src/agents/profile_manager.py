import json
from typing import Dict, Any


class ProfileManager:
    """Manages user profile data."""

    def __init__(self, profile_path: str):
        """Initialize with the path to the profile JSON."""
        self.profile_path = profile_path
        self.profile = {}

    def load_profile(self) -> Dict[str, Any]:
        """Load profile from JSON file."""
        try:
            with open(self.profile_path, 'r', encoding='utf-8') as f:
                self.profile = json.load(f)
            return self.profile
        except Exception as e:
            raise ValueError(f"Failed to load profile: {e}")

    def get_param(self, key: str) -> Any:
        """Get a specific profile parameter."""
        return self.profile.get(key)

    def update_param(self, key: str, value: Any) -> None:
        """Update a profile parameter and save to file."""
        self.profile[key] = value
        with open(self.profile_path, 'w', encoding='utf-8') as f:
            json.dump(self.profile, f, indent=2, ensure_ascii=False)