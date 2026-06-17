import sqlite3
import uuid

from langgraph.checkpoint.sqlite import SqliteSaver

from .config import DB_PATH

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
checkpointer = SqliteSaver(conn)


def init_registry() -> None:
    conn.execute(
        "CREATE TABLE IF NOT EXISTS users ("
        "user_id TEXT PRIMARY KEY, username TEXT UNIQUE)"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS chats ("
        "chat_id TEXT PRIMARY KEY, user_id TEXT, title TEXT, "
        "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
    )
    conn.commit()


def get_or_create_user(username: str) -> str:
    row = conn.execute(
        "SELECT user_id FROM users WHERE username = ?", (username,)
    ).fetchone()
    if row:
        return row[0]
    user_id = uuid.uuid4().hex
    conn.execute(
        "INSERT INTO users (user_id, username) VALUES (?, ?)", (user_id, username)
    )
    conn.commit()
    return user_id


def list_chats(user_id: str) -> list[tuple[str, str]]:
    return conn.execute(
        "SELECT chat_id, title FROM chats WHERE user_id = ? ORDER BY created_at",
        (user_id,),
    ).fetchall()


def create_chat(user_id: str, title: str) -> str:
    chat_id = uuid.uuid4().hex
    conn.execute(
        "INSERT INTO chats (chat_id, user_id, title) VALUES (?, ?, ?)",
        (chat_id, user_id, title),
    )
    conn.commit()
    return chat_id
