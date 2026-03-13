"""Data model for AI Memory entries."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class AIMemory:
    """Represents a piece of long-term AI memory."""

    id: Optional[int] = None
    memory_type: str = ""  # conversation_history, habit_patterns, journal_summaries
    content: str = ""
    embedding: str = ""
    created_at: str = ""
    updated_at: str = ""
