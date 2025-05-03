import yaml
from mastodon import Mastodon
from langgraph.checkpoint.sqlite import SqliteSaver
from src.mastodon.listener import BotStreamListener
from src.graph.logic_graph import build_graph
from src.models.user_profile import UserProfile
import os


def load_config(config_path: str) -> dict:
    """Загружает конфигурацию из YAML-файла."""
    with open(config_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)


def main():
    config = load_config('config/config.yaml')

    for var, val in config['langsmith'].items():
        os.environ[var] = val

    profile = UserProfile(
        **config['user_profile']
    )

    mastodon = Mastodon(**config['mastodon'])

    with SqliteSaver.from_conn_string(config['app']['sqlite_path']) as memory:
        graph = build_graph(
            profile=profile,
            mastodon=mastodon,
            checkpointer=memory,
            llm_config=config['llm']
        )
        from langchain_core.runnables.graph import CurveStyle, MermaidDrawMethod, NodeStyles
        from PIL import Image
        from io import BytesIO

        Image.open(BytesIO(graph.get_graph().draw_mermaid_png(draw_method=MermaidDrawMethod.API))).save('data/agent.png', 'PNG')

        listener = BotStreamListener(graph, profile, mastodon)
        mastodon.stream_user(listener)


if __name__ == "__main__":
    main()