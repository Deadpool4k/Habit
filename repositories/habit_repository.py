"""Repository for habit and habit_entry CRUD operations."""
import calendar
from datetime import date, timedelta
from typing import Optional

from database.database import get_connection
from models.habit import Habit
from models.habit_entry import HabitEntry


def _row_to_habit(row) -> Habit:
    return Habit(
        id=row["id"],
        name=row["name"],
        habit_type=row["habit_type"],
        color=row["color"],
        icon=row["icon"],
        target_value=row["target_value"],
        unit=row["unit"],
        created_at=row["created_at"],
        is_active=row["is_active"],
    )


def _row_to_entry(row) -> HabitEntry:
    return HabitEntry(
        id=row["id"],
        habit_id=row["habit_id"],
        date=row["date"],
        value=row["value"],
        notes=row["notes"] or "",
        created_at=row["created_at"],
    )


def get_all_habits() -> list[Habit]:
    """Return all active habits ordered by name."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM habits WHERE is_active = 1 ORDER BY name"
    ).fetchall()
    return [_row_to_habit(r) for r in rows]


def get_habit_by_id(habit_id: int) -> Optional[Habit]:
    """Return a single habit by primary key, or None."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM habits WHERE id = ?", (habit_id,)).fetchone()
    return _row_to_habit(row) if row else None


def create_habit(habit: Habit) -> int:
    """Insert a new habit and return its new id."""
    conn = get_connection()
    cur = conn.execute(
        """INSERT INTO habits (name, habit_type, color, icon, target_value, unit)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (habit.name, habit.habit_type, habit.color, habit.icon,
         habit.target_value, habit.unit),
    )
    conn.commit()
    return cur.lastrowid


def update_habit(habit: Habit) -> None:
    """Update an existing habit record."""
    conn = get_connection()
    conn.execute(
        """UPDATE habits
           SET name=?, habit_type=?, color=?, icon=?, target_value=?, unit=?, is_active=?
           WHERE id=?""",
        (habit.name, habit.habit_type, habit.color, habit.icon,
         habit.target_value, habit.unit, habit.is_active, habit.id),
    )
    conn.commit()


def delete_habit(habit_id: int) -> None:
    """Soft-delete a habit by marking it inactive."""
    conn = get_connection()
    conn.execute("UPDATE habits SET is_active = 0 WHERE id = ?", (habit_id,))
    conn.commit()


def get_entry(habit_id: int, entry_date: str) -> Optional[HabitEntry]:
    """Return the entry for a specific habit and date, or None."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM habit_entries WHERE habit_id = ? AND date = ?",
        (habit_id, entry_date),
    ).fetchone()
    return _row_to_entry(row) if row else None


def toggle_entry(habit_id: int, entry_date: str) -> bool:
    """Toggle a YES_NO entry; return True if now completed, False if deleted."""
    existing = get_entry(habit_id, entry_date)
    conn = get_connection()
    if existing:
        conn.execute(
            "DELETE FROM habit_entries WHERE habit_id = ? AND date = ?",
            (habit_id, entry_date),
        )
        conn.commit()
        return False
    conn.execute(
        "INSERT INTO habit_entries (habit_id, date, value) VALUES (?, ?, 1)",
        (habit_id, entry_date),
    )
    conn.commit()
    return True


def set_entry_value(habit_id: int, entry_date: str, value: float) -> None:
    """Upsert a numeric value for a habit entry."""
    conn = get_connection()
    existing = get_entry(habit_id, entry_date)
    if existing:
        conn.execute(
            "UPDATE habit_entries SET value = ? WHERE habit_id = ? AND date = ?",
            (value, habit_id, entry_date),
        )
    else:
        conn.execute(
            "INSERT INTO habit_entries (habit_id, date, value) VALUES (?, ?, ?)",
            (habit_id, entry_date, value),
        )
    conn.commit()


def get_entries_for_month(habit_id: int, year: int, month: int) -> list[HabitEntry]:
    """Return all entries for a habit within a calendar month."""
    start = f"{year:04d}-{month:02d}-01"
    last_day = calendar.monthrange(year, month)[1]
    end = f"{year:04d}-{month:02d}-{last_day:02d}"
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM habit_entries WHERE habit_id = ? AND date BETWEEN ? AND ?",
        (habit_id, start, end),
    ).fetchall()
    return [_row_to_entry(r) for r in rows]


def get_all_entries_for_month(year: int, month: int) -> dict[int, list[str]]:
    """Return a mapping of habit_id → list of completed date strings for the month."""
    start = f"{year:04d}-{month:02d}-01"
    last_day = calendar.monthrange(year, month)[1]
    end = f"{year:04d}-{month:02d}-{last_day:02d}"
    conn = get_connection()
    rows = conn.execute(
        "SELECT habit_id, date FROM habit_entries WHERE date BETWEEN ? AND ?",
        (start, end),
    ).fetchall()
    result: dict[int, list[str]] = {}
    for r in rows:
        result.setdefault(r["habit_id"], []).append(r["date"])
    return result


def get_streak(habit_id: int) -> int:
    """Return the current consecutive-day streak for a habit."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT date FROM habit_entries WHERE habit_id = ? ORDER BY date DESC",
        (habit_id,),
    ).fetchall()
    if not rows:
        return 0
    dates = {r["date"] for r in rows}
    streak = 0
    check = date.today()
    while check.isoformat() in dates:
        streak += 1
        check -= timedelta(days=1)
    # Also count yesterday-based streak (if today not yet logged)
    if streak == 0:
        check = date.today() - timedelta(days=1)
        while check.isoformat() in dates:
            streak += 1
            check -= timedelta(days=1)
    return streak
