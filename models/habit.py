"""Data model for a Habit."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Habit:
    """Represents a trackable habit."""

    id: Optional[int] = None
    name: str = ""
    habit_type: str = "YES_NO"  # YES_NO, COUNTER, TIMER, MEASURABLE
    color: str = "#6366f1"
    icon: str = "⭐"
    target_value: float = 1.0
    unit: str = ""
    created_at: str = ""
    is_active: int = 1
