"""Repository for statistics / aggregation queries."""
import calendar
from datetime import date, timedelta

from database.database import get_connection


def get_weekly_completion() -> list[dict]:
    """Return completion counts for the last 7 days.

    Each element: {date: str, completed: int, total: int}
    """
    conn = get_connection()
    today = date.today()
    result = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_str = day.isoformat()
        total = conn.execute(
            "SELECT COUNT(*) FROM habits WHERE is_active = 1"
        ).fetchone()[0]
        completed = conn.execute(
            "SELECT COUNT(*) FROM habit_entries WHERE date = ?", (day_str,)
        ).fetchone()[0]
        result.append({"date": day_str, "completed": completed, "total": total})
    return result


def get_monthly_completion(year: int, month: int) -> list[dict]:
    """Return completion counts for each day in the given month.

    Each element: {date: str, completed: int, total: int}
    """
    conn = get_connection()
    last_day = calendar.monthrange(year, month)[1]
    total_habits = conn.execute(
        "SELECT COUNT(*) FROM habits WHERE is_active = 1"
    ).fetchone()[0]
    result = []
    for day in range(1, last_day + 1):
        day_str = f"{year:04d}-{month:02d}-{day:02d}"
        completed = conn.execute(
            "SELECT COUNT(DISTINCT habit_id) FROM habit_entries WHERE date = ?",
            (day_str,),
        ).fetchone()[0]
        result.append(
            {"date": day_str, "completed": completed, "total": total_habits}
        )
    return result


def get_activity_heatmap(year: int, month: int) -> dict[str, int]:
    """Return a mapping of date_str → number of habits completed that day."""
    conn = get_connection()
    last_day = calendar.monthrange(year, month)[1]
    start = f"{year:04d}-{month:02d}-01"
    end = f"{year:04d}-{month:02d}-{last_day:02d}"
    rows = conn.execute(
        """SELECT date, COUNT(DISTINCT habit_id) AS cnt
           FROM habit_entries
           WHERE date BETWEEN ? AND ?
           GROUP BY date""",
        (start, end),
    ).fetchall()
    return {r["date"]: r["cnt"] for r in rows}
