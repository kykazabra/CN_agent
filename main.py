import yaml
from mastodon import Mastodon
from src.mastodon.listener import BotStreamListener
from src.graph.logic_graph import build_graph
from src.models.user_profile import UserProfile


def load_config(config_path: str) -> dict:
    """Загружает конфигурацию из YAML-файла."""
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)


def main():
    config = load_config('config/config.yaml')

    profile = UserProfile(
        interests=config['user_profile']['interests'],
        post_frequency=config['user_profile']['post_frequency'],
        style=config['user_profile']['style']
    )

    mastodon = Mastodon(
        access_token=config['mastodon']['access_token'],
        api_base_url=config['mastodon']['api_base_url']
    )

    graph = build_graph(profile, mastodon, config['llm'])

    listener = BotStreamListener(graph, profile, mastodon)
    mastodon.stream_user(listener)


if __name__ == "__main__":
    main()