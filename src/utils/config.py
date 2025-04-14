import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")

# Action probabilities
POST_PROBABILITY = 0.7
COMMENT_PROBABILITY = 0.3
SUBSCRIBE_PROBABILITY = 0.1

# Active hours
ACTIVE_HOURS = [18, 19, 20, 21, 22]