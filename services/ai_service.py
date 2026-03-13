"""AI chat service integrating OpenAI API with RAG from memory."""
from datetime import date, timedelta
from config import load_config
import repositories.memory_repository as mem_repo
from ai.ai_chat import get_system_prompt, format_messages_for_api, build_context_from_memories
from ai.ai_memory_system import retrieve_relevant_memories
from database.database import get_connection

_MOOD_MAP = {1: "very sad", 2: "sad", 3: "neutral", 4: "happy", 5: "very happy"}
# Maximum characters of journal text sent to AI to keep prompts concise
_JOURNAL_TEXT_LIMIT = 300


def _build_live_context() -> str:
    """Query SQLite for today's habits, journal, mood and return as context string."""
    today = date.today().isoformat()
    conn = get_connection()
    lines = [f"=== Live Data (today: {today}) ==="]

    # Today's completed habits
    try:
        rows = conn.execute(
            """SELECT h.name, h.habit_type, he.value
               FROM habit_entries he
               JOIN habits h ON h.id = he.habit_id
               WHERE he.date = ? AND h.is_active = 1""",
            (today,)
        ).fetchall()
        if rows:
            lines.append(f"\nHabits completed today ({len(rows)}):")
            for r in rows:
                lines.append(f"  - {r['name']} ({r['habit_type']}): value={r['value']}")
        else:
            lines.append("\nNo habits completed today yet.")
    except Exception:
        pass

    # All active habits (so AI knows what exists)
    try:
        all_habits = conn.execute(
            "SELECT name, habit_type, target_value, unit FROM habits WHERE is_active = 1"
        ).fetchall()
        if all_habits:
            lines.append(f"\nAll tracked habits ({len(all_habits)} total):")
            for h in all_habits:
                lines.append(f"  - {h['name']} ({h['habit_type']}, target: {h['target_value']} {h['unit']})")
    except Exception:
        pass

    # Last 7 days completion summary
    try:
        week_lines = []
        for i in range(6, -1, -1):
            d = (date.today() - timedelta(days=i)).isoformat()
            count = conn.execute(
                "SELECT COUNT(*) as c FROM habit_entries WHERE date = ?", (d,)
            ).fetchone()["c"]
            total = conn.execute(
                "SELECT COUNT(*) as c FROM habits WHERE is_active = 1"
            ).fetchone()["c"]
            label = "today" if i == 0 else f"{i}d ago"
            week_lines.append(f"  {d} ({label}): {count}/{total} habits")
        lines.append("\nLast 7 days habit completion:")
        lines.extend(week_lines)
    except Exception:
        pass

    # Today's journal entry
    try:
        journal = conn.execute(
            "SELECT text, mood, stress_level, energy_level FROM journal_entries WHERE date = ?",
            (today,)
        ).fetchone()
        if journal:
            lines.append(f"\nToday's journal entry:")
            if journal["text"]:
                lines.append(f"  Text: {journal['text'][:_JOURNAL_TEXT_LIMIT]}")
            lines.append(f"  Mood: {journal['mood']}/5 ({_MOOD_MAP.get(journal['mood'], '?')})")
            lines.append(f"  Stress level: {journal['stress_level']}/5")
            lines.append(f"  Energy level: {journal['energy_level']}/5")
        else:
            lines.append("\nNo journal entry for today yet.")
    except Exception:
        pass

    # Recent journal entries (last 3 days)
    try:
        recent = conn.execute(
            """SELECT date, mood, stress_level, energy_level, text
               FROM journal_entries
               WHERE date < ?
               ORDER BY date DESC LIMIT 3""",
            (today,)
        ).fetchall()
        if recent:
            lines.append("\nRecent journal entries (last 3 days):")
            for r in recent:
                lines.append(f"  {r['date']}: mood={r['mood']}/5, stress={r['stress_level']}/5, energy={r['energy_level']}/5")
    except Exception:
        pass

    return "\n".join(lines)


def send_message(user_input: str, page=None) -> str:
    """Send a user message, build context, call OpenAI, persist exchange."""
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

    # Build live context from database
    live_context = _build_live_context()

    # Retrieve relevant memories for RAG context
    memories = retrieve_relevant_memories(user_input, top_k=5)
    rag_context = build_context_from_memories(memories)

    # Combine live data + RAG memories
    full_context = live_context
    if rag_context:
        full_context += f"\n\n=== Relevant Memories ===\n{rag_context}"

    system_prompt = get_system_prompt(full_context)

    # Load recent conversation history
    history = mem_repo.get_all_messages(limit=20)
    messages = format_messages_for_api(history, system_prompt)
    messages.append({"role": "user", "content": user_input})

    # Persist the user message
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
