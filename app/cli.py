from langchain_core.messages import HumanMessage

from .graph import build_app
from .db import init_registry, get_or_create_user, list_chats, create_chat


def choose_thread_id() -> tuple[str, str, str]:
    username = input("Who are you? (username): ").strip() or "guest"
    user_id = get_or_create_user(username)

    chats = list_chats(user_id)
    if chats:
        print("\nYour chats:")
        for i, (_, title) in enumerate(chats, start=1):
            print(f"  {i}. {title}")
        choice = input(
            "Pick a number to resume, or press Enter for a NEW chat: "
        ).strip()
        if choice.isdigit() and 1 <= int(choice) <= len(chats):
            chat_id, title = chats[int(choice) - 1]
            print(f"Resuming '{title}'.\n")
            return chat_id, user_id, username

    title = input("Title for the new chat (or Enter for 'Untitled'): ").strip() or "Untitled"
    chat_id = create_chat(user_id, title)
    print(f"Starting new chat '{title}'.\n")
    return chat_id, user_id, username


def run():
    init_registry()
    app = build_app()

    thread_id, user_id, username = choose_thread_id()
    config = {"configurable": {"thread_id": thread_id}}
    context = {"user_id": user_id, "username": username}

    print("Tutor — type 'quit' to exit.\n")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"quit", "exit"}:
            break

        result = app.invoke(
            {"messages": [HumanMessage(content=user_input)]},
            config=config,
            context=context,
        )
        print("Bot:", result["last_response"], "\n")
