import os

HAIKU_MODEL = "claude-haiku-4-5"
SONNET_MODEL = "claude-sonnet-4-6"

HAIKU_MAX_TOKENS = 1024
SONNET_MAX_TOKENS = 4096

HISTORY_TOKEN_BUDGET = 4000
MAX_RETRIES = 2

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://chatbot:chatbot@localhost:5432/chatbot"
)
