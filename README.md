# LangGraph Tutor — a learning project

A tutor chatbot built on LangGraph that **guards, reasons, uses tools, and self-checks**.
It demonstrates state, nodes, conditional routing, tools, structured output,
persistence (checkpointer), per-user/per-chat isolation, and LangSmith tracing.

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env      
python chatbot.py
```

Type messages; `quit` to exit. State persists to `chatbot.db`, so resuming a chat
restores its history.


### Nodes

- **intent** — runs first on every message. Classifies the latest human message
  into `hazardous | factual | conceptual | quiz | general` (Haiku + structured
  output) and resets `retry_count` to 0.
- **reject** — fixed refusal message, no LLM reasoning. Only for `hazardous`.
- **agent** — main reasoning. Trims history to a token budget, prepends the system
  prompt, calls Sonnet with tools bound. Emits a tool call or a final answer.
- **tools** — prebuilt `ToolNode`. Runs whatever tool the agent called, returns the
  result so the agent can continue.
- **evaluator** — grades the final answer (Haiku + structured output → `{passed,
  feedback}`). Pass → end. Fail with retries left → inject feedback and send back to
  agent. Out of retries (`MAX_RETRIES=2`) → force-pass so the graph always ends.


