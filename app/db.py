import uuid

import psycopg
from psycopg.rows import dict_row
from langgraph.checkpoint.postgres import PostgresSaver

from .config import DATABASE_URL

_checkpointer_conn = psycopg.connect(
    DATABASE_URL, autocommit=True, prepare_threshold=0, row_factory=dict_row
)
checkpointer = PostgresSaver(_checkpointer_conn)

conn = psycopg.connect(DATABASE_URL, autocommit=True)


def init_registry() -> None:
    checkpointer.setup()
    conn.execute(
        "CREATE TABLE IF NOT EXISTS users ("
        "user_id TEXT PRIMARY KEY, username TEXT UNIQUE)"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS chats ("
        "chat_id TEXT PRIMARY KEY, user_id TEXT, title TEXT, "
        "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
    )


def get_or_create_user(username: str) -> str:
    row = conn.execute(
        "SELECT user_id FROM users WHERE username = %s", (username,)
    ).fetchone()
    if row:
        return row[0]
    user_id = uuid.uuid4().hex
    conn.execute(
        "INSERT INTO users (user_id, username) VALUES (%s, %s)", (user_id, username)
    )
    return user_id


def list_chats(user_id: str) -> list[tuple[str, str]]:
    return conn.execute(
        "SELECT chat_id, title FROM chats WHERE user_id = %s ORDER BY created_at",
        (user_id,),
    ).fetchall()


def create_chat(user_id: str, title: str) -> str:
    chat_id = uuid.uuid4().hex
    conn.execute(
        "INSERT INTO chats (chat_id, user_id, title) VALUES (%s, %s, %s)",
        (chat_id, user_id, title),
    )
    return chat_id
