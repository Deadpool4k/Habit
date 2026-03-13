"""Data model for a Mood Entry."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class MoodEntry:
    """Represents a standalone mood check-in."""

    id: Optional[int] = None
    date: str = ""
    mood: int = 3
    notes: str = ""
    created_at: str = ""
