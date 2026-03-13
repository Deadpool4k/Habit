"""Business logic for habit management."""
from datetime import date
from typing import Optional

from models.habit import Habit
import repositories.habit_repository as repo


def get_all_habits() -> list[Habit]:
    """Return all active habits."""
    return repo.get_all_habits()


def create_habit(
    name: str,
    habit_type: str = "YES_NO",
    color: str = "#6366f1",
    icon: str = "⭐",
    target_value: float = 1.0,
    unit: str = "",
) -> Habit:
    """Create and persist a new habit; return the saved object."""
    h = Habit(
        name=name,
        habit_type=habit_type,
        color=color,
        icon=icon,
        target_value=target_value,
        unit=unit,
    )
    new_id = repo.create_habit(h)
    h.id = new_id
    return h


def update_habit(habit: Habit) -> None:
    """Persist changes to an existing habit."""
    repo.update_habit(habit)


def delete_habit(habit_id: int) -> None:
    """Soft-delete a habit."""
    repo.delete_habit(habit_id)


def toggle_habit(habit_id: int, entry_date: Optional[str] = None) -> bool:
    """Toggle today's (or given date's) completion; return new state."""
    if entry_date is None:
        entry_date = date.today().isoformat()
    return repo.toggle_entry(habit_id, entry_date)


def get_habits_for_month(year: int, month: int) -> dict:
    """Return {habit_id: [date_str, ...]} for the given month."""
    return repo.get_all_entries_for_month(year, month)


def calculate_streak(habit_id: int) -> int:
    """Return the current streak in days for a habit."""
    return repo.get_streak(habit_id)


def get_today_progress() -> tuple[int, int]:
    """Return (completed_today, total_active_habits)."""
    habits = repo.get_all_habits()
    total = len(habits)
    today = date.today().isoformat()
    completed = sum(
        1 for h in habits if repo.get_entry(h.id, today) is not None
    )
    return completed, total
