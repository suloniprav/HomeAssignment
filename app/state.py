from typing import Annotated

from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


class State(TypedDict):
    messages: Annotated[list, add_messages]
    last_response: str
    intent: str
    retry_count: int
    eval_passed: bool


class GraphContext(TypedDict):
    user_id: str
    username: str
