from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

from .state import State
from .tools import TOOLS
from .db import checkpointer
from .nodes import (
    intent,
    reject,
    agent,
    evaluator,
    route_intent,
    route_agent,
    route_evaluator,
)


def build_app():
    graph = StateGraph(State)

    graph.add_node("intent", intent)
    graph.add_node("reject", reject)
    graph.add_node("agent", agent)
    graph.add_node("tools", ToolNode(TOOLS))
    graph.add_node("evaluator", evaluator)

    graph.add_edge(START, "intent")
    graph.add_conditional_edges(
        "intent", route_intent, {"reject": "reject", "agent": "agent"}
    )
    graph.add_edge("reject", END)
    graph.add_conditional_edges(
        "agent", route_agent, {"tools": "tools", "evaluator": "evaluator"}
    )
    graph.add_edge("tools", "agent")
    graph.add_conditional_edges(
        "evaluator", route_evaluator, {"agent": "agent", END: END}
    )

    return graph.compile(checkpointer=checkpointer)
