from langchain_anthropic import ChatAnthropic

from .config import (
    HAIKU_MODEL,
    SONNET_MODEL,
    HAIKU_MAX_TOKENS,
    SONNET_MAX_TOKENS,
)
from .schemas import IntentResult, EvalResult
from .tools import TOOLS

haiku = ChatAnthropic(model=HAIKU_MODEL, max_tokens=HAIKU_MAX_TOKENS)
sonnet = ChatAnthropic(model=SONNET_MODEL, max_tokens=SONNET_MAX_TOKENS)

intent_llm = haiku.with_structured_output(IntentResult)
evaluator_llm = haiku.with_structured_output(EvalResult)
agent_llm = sonnet.bind_tools(TOOLS)
