import sys

sys.path.append('..')

from src.models.user_profile import UserProfile
from src.graph.logic_graph import build_graph
from tests.mastodon_emulation import MastodonEmulator
from tests.bench import MastodonBenchmark
from langgraph.checkpoint.sqlite import SqliteSaver
from main import load_config
from langchain_openai import ChatOpenAI
import os


config = load_config('../config/config.yaml')

for var, val in config['langsmith'].items():
    os.environ[var] = val

profile = UserProfile(
    **config['user_profile']
)

mastodon = MastodonEmulator()

if os.path.exists('../data/test.sqlite'):
    os.remove('../data/test.sqlite')

with SqliteSaver.from_conn_string('../data/test.sqlite') as memory:
    graph = build_graph(
        profile=profile,
        mastodon=mastodon,
        checkpointer=memory,
        llm_config=config['llm']
    )

    c = config['llm']
    c['model'] = 'gpt-4o'

    judge = ChatOpenAI(**c)

    benchmark = MastodonBenchmark(graph, profile, mastodon, judge)
    benchmark.load_bench('inputs/bench_tests.json')

    benchmark.run()
