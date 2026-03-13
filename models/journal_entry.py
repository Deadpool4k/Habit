"""Data model for a Journal Entry."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class JournalEntry:
    """Represents a daily journal entry with mood and wellness metrics."""

    id: Optional[int] = None
    date: str = ""
    text: str = ""
    mood: int = 3
    stress_level: int = 3
    energy_level: int = 3
    created_at: str = ""
    updated_at: str = ""
