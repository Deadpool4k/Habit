"""Helpers for building OpenAI chat prompts."""


def get_system_prompt(context: str = "") -> str:
    """Return the system prompt, optionally enriched with live data and RAG context."""
    base = (
        "You are a supportive AI wellness coach integrated into a habit and mood "
        "tracking application. You have DIRECT ACCESS to the user's real-time data "
        "including their habits, journal entries, mood, stress levels, and energy levels. "
        "When the user asks about their habits, mood, stress, energy or journal — use the "
        "live data provided in the context below to give accurate, specific answers. "
        "Be empathetic, concise, and actionable. Celebrate streaks and progress. "
        "Gently encourage when the user is struggling. Always respond in the same "
        "language the user writes in."
    )
    if context:
        return f"{base}\n\n{context}"
    return base


def format_messages_for_api(
    history: list[dict], system_prompt: str
) -> list[dict]:
    """Convert stored message history into the OpenAI messages array format."""
    messages = [{"role": "system", "content": system_prompt}]
    for msg in history:
        if msg["role"] in ("user", "assistant"):
            messages.append({"role": msg["role"], "content": msg["content"]})
    return messages


def build_context_from_memories(memories: list[str]) -> str:
    """Join memory strings into a single context block."""
    if not memories:
        return ""
    return "\n".join(f"- {m}" for m in memories)
