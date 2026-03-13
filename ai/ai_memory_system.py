"""AI memory system: save, retrieve, and summarise long-term memories."""
from datetime import date, timedelta

import repositories.memory_repository as mem_repo
import repositories.journal_repository as journal_repo
import repositories.habit_repository as habit_repo
from ai.embeddings_search import find_relevant_memories


def save_memory(memory_type: str, content: str) -> None:
    """Persist a new memory entry."""
    mem_repo.add_memory(memory_type, content)


def retrieve_relevant_memories(query: str, top_k: int = 5) -> list[str]:
    """Return the top-k relevant memory content strings for *query*."""
    all_memories = mem_repo.get_all_memories()
    if not all_memories:
        return []
    relevant = find_relevant_memories(query, all_memories, top_k=top_k)
    return [m.content for m in relevant]


def summarize_recent_journal(days: int = 7) -> str:
    """Build a human-readable summary of the last *days* journal entries."""
    entries = journal_repo.get_recent_entries(days)
    if not entries:
        return "No journal entries in the last {} days.".format(days)

    mood_labels = {1: "very sad", 2: "sad", 3: "neutral", 4: "happy", 5: "very happy"}
    lines = []
    for entry in entries:
        mood_label = mood_labels.get(entry.mood, "unknown")
        snippet = entry.text[:120].replace("\n", " ") if entry.text else "(no text)"
        lines.append(
            f"• {entry.date}: mood={mood_label}, stress={entry.stress_level}/5, "
            f"energy={entry.energy_level}/5 — {snippet}"
        )
    return "Recent journal summary:\n" + "\n".join(lines)


def extract_habit_patterns() -> str:
    """Build a summary of current habit streaks and completion rates."""
    habits = habit_repo.get_all_habits()
    if not habits:
        return "No habits tracked yet."

    lines = []
    for habit in habits:
        streak = habit_repo.get_streak(habit.id)
        lines.append(f"• {habit.icon} {habit.name}: {streak}-day streak")
    return "Current habit patterns:\n" + "\n".join(lines)
