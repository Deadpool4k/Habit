"""AI chat service integrating OpenAI API with RAG from memory."""
from config import load_config
import repositories.memory_repository as mem_repo
from ai.ai_chat import get_system_prompt, format_messages_for_api, build_context_from_memories
from ai.ai_memory_system import retrieve_relevant_memories


def send_message(user_input: str, page=None) -> str:
    """Send a user message, build context, call OpenAI, persist exchange.

    Returns the assistant reply string.  Handles missing API key gracefully.
    """
    config = load_config()
    api_key = config.get("openai_api_key", "").strip()

    if not api_key:
        return (
            "⚠️ No OpenAI API key configured.\n\n"
            "Please go to **Settings** and enter your OpenAI API key to enable "
            "AI chat functionality."
        )

    try:
        from openai import OpenAI
    except ImportError:
        return "⚠️ The 'openai' package is not installed. Run: pip install openai"

    # Retrieve relevant memories for RAG context
    memories = retrieve_relevant_memories(user_input, top_k=5)
    context = build_context_from_memories(memories)
    system_prompt = get_system_prompt(context)

    # Load recent conversation history
    history = mem_repo.get_all_messages(limit=20)
    messages = format_messages_for_api(history, system_prompt)
    messages.append({"role": "user", "content": user_input})

    # Persist the user message first
    mem_repo.add_message("user", user_input)

    try:
        client = OpenAI(api_key=api_key)
        model = config.get("openai_model", "gpt-4o")
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=1024,
            temperature=0.7,
        )
        reply = response.choices[0].message.content.strip()
    except Exception as exc:
        reply = f"⚠️ OpenAI API error: {exc}"

    mem_repo.add_message("assistant", reply)
    return reply
