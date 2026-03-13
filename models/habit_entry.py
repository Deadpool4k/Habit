"""Data model for a Habit Entry (a single day's completion record)."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class HabitEntry:
    """Represents one day's recorded value for a habit."""

    id: Optional[int] = None
    habit_id: int = 0
    date: str = ""
    value: float = 1.0
    notes: str = ""
    created_at: str = ""
