import datetime

from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langchain_anthropic import ChatAnthropic

from .config import HAIKU_MODEL

NOTES_FILE = "notes.md"


@tool
def search_web(query: str) -> str:
    """Search the web for up-to-date information on any topic.

    Use when the user asks about something current, version-specific, or
    anything you are not fully confident about.
    """
    try:
        from ddgs import DDGS

        results = DDGS().text(query, max_results=5)
        if not results:
            return "No results found."
        return "\n\n".join(
            f"{r.get('title', '')}\n{r.get('body', '')}\n{r.get('href', '')}"
            for r in results
        )
    except Exception as e:
        return (
            f"Search unavailable ({e}). Answer from your own knowledge and be "
            "clear about any uncertainty."
        )


@tool
def save_note(concept: str, explanation: str) -> str:
    """Save an important concept and its explanation to notes.md.

    Use after explaining something the user should remember long-term.

    Args:
        concept: Short name/title (e.g. "Gradient Descent").
        explanation: Concise explanation to save (2-4 sentences).
    """
    try:
        with open(NOTES_FILE) as f:
            existing = f.read()
    except FileNotFoundError:
        existing = ""

    saved_concepts = {
        line[3:].strip().lower()
        for line in existing.splitlines()
        if line.startswith("## ")
    }
    if concept.strip().lower() in saved_concepts:
        return f"'{concept}' is already in {NOTES_FILE}; skipped."

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"\n## {concept}\n*Saved: {timestamp}*\n\n{explanation}\n"
    with open(NOTES_FILE, "a") as f:
        f.write(entry)
    return f"Saved '{concept}' to {NOTES_FILE}."


_flashcard_llm = ChatAnthropic(model=HAIKU_MODEL, max_tokens=1024)


@tool
def generate_flashcards(topic: str, num_cards: int = 4) -> str:
    """Generate flashcard-style Q&A pairs to help the user self-test.

    Use when the user asks to be quizzed or has finished a topic.

    Args:
        topic: Subject to generate flashcards for.
        num_cards: How many cards to generate (default 4).
    """
    prompt = (
        f"Generate {num_cards} flashcard Q&A pairs about: {topic}\n\n"
        "Format each card exactly like this:\n"
        "Q: <question>\nA: <answer>\n\n"
        "Keep answers concise (1-3 sentences). Cover the most important concepts."
    )
    result = _flashcard_llm.invoke([HumanMessage(content=prompt)])
    return result.content


TOOLS = [search_web, save_note, generate_flashcards]
