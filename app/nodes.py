from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage,
    trim_messages,
)
from langchain_core.messages.utils import count_tokens_approximately
from langgraph.graph import END
from langgraph.runtime import Runtime

from .config import HISTORY_TOKEN_BUDGET, MAX_RETRIES
from .models import intent_llm, evaluator_llm, agent_llm
from .prompts import SYSTEM_PROMPT, INTENT_PROMPT, EVALUATOR_PROMPT, REJECT_MESSAGE
from .state import State, GraphContext


def _latest_human(messages) -> str:
    for message in reversed(messages):
        if isinstance(message, HumanMessage):
            return message.content
    return ""


def intent(state: State, runtime: Runtime[GraphContext]) -> dict:
    question = _latest_human(state["messages"])
    result = intent_llm.invoke(
        [SystemMessage(content=INTENT_PROMPT), HumanMessage(content=question)]
    )
    return {"intent": result.category, "retry_count": 0, "eval_passed": False}


def reject(state: State, runtime: Runtime[GraphContext]) -> dict:
    return {"messages": [AIMessage(content=REJECT_MESSAGE)], "last_response": REJECT_MESSAGE}


def agent(state: State, runtime: Runtime[GraphContext]) -> dict:
    history = trim_messages(
        state["messages"],
        max_tokens=HISTORY_TOKEN_BUDGET,
        strategy="last",
        token_counter=count_tokens_approximately,
        start_on="human",
        allow_partial=False,
    )
    username = runtime.context["username"]
    system_prompt = f"{SYSTEM_PROMPT}\n\nYou are currently tutoring {username}."
    conversation = [SystemMessage(content=system_prompt)] + history
    response = agent_llm.invoke(conversation)
    return {"messages": [response], "last_response": response.content}


def evaluator(state: State, runtime: Runtime[GraphContext]) -> dict:
    question = _latest_human(state["messages"])
    answer = state["last_response"]
    result = evaluator_llm.invoke(
        [
            SystemMessage(content=EVALUATOR_PROMPT),
            HumanMessage(content=f"Question:\n{question}\n\nAnswer:\n{answer}"),
        ]
    )

    if result.passed:
        return {"eval_passed": True}

    retry_count = state.get("retry_count", 0)
    if retry_count >= MAX_RETRIES:
        return {"eval_passed": True}

    feedback = (
        "Your previous answer did not meet the quality bar. "
        f"Reviewer feedback: {result.feedback} "
        "Please write an improved answer that addresses this feedback."
    )
    return {
        "eval_passed": False,
        "retry_count": retry_count + 1,
        "messages": [HumanMessage(content=feedback)],
    }


def route_intent(state: State) -> str:
    return "reject" if state["intent"] == "hazardous" else "agent"


def route_agent(state: State) -> str:
    last = state["messages"][-1]
    if getattr(last, "tool_calls", None):
        return "tools"
    return "evaluator"


def route_evaluator(state: State):
    return END if state["eval_passed"] else "agent"
