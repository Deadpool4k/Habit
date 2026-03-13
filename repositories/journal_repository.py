"""Repository for journal_entry CRUD operations."""
from datetime import date, timedelta
from typing import Optional

from database.database import get_connection
from models.journal_entry import JournalEntry


def _row_to_entry(row) -> JournalEntry:
    return JournalEntry(
        id=row["id"],
        date=row["date"],
        text=row["text"] or "",
        mood=row["mood"],
        stress_level=row["stress_level"],
        energy_level=row["energy_level"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def get_entry_by_date(entry_date: str) -> Optional[JournalEntry]:
    """Return the journal entry for the given date string, or None."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM journal_entries WHERE date = ?", (entry_date,)
    ).fetchone()
    return _row_to_entry(row) if row else None


def create_or_update_entry(entry: JournalEntry) -> JournalEntry:
    """Insert a new entry or update an existing one; return the saved entry."""
    conn = get_connection()
    existing = get_entry_by_date(entry.date)
    if existing:
        conn.execute(
            """UPDATE journal_entries
               SET text=?, mood=?, stress_level=?, energy_level=?,
                   updated_at=datetime('now')
               WHERE date=?""",
            (entry.text, entry.mood, entry.stress_level, entry.energy_level,
             entry.date),
        )
        conn.commit()
        return get_entry_by_date(entry.date)
    cur = conn.execute(
        """INSERT INTO journal_entries (date, text, mood, stress_level, energy_level)
           VALUES (?, ?, ?, ?, ?)""",
        (entry.date, entry.text, entry.mood, entry.stress_level, entry.energy_level),
    )
    conn.commit()
    row = conn.execute(
        "SELECT * FROM journal_entries WHERE id = ?", (cur.lastrowid,)
    ).fetchone()
    return _row_to_entry(row)


def get_all_entries(limit: int = 50) -> list[JournalEntry]:
    """Return up to *limit* journal entries ordered newest-first."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM journal_entries ORDER BY date DESC LIMIT ?", (limit,)
    ).fetchall()
    return [_row_to_entry(r) for r in rows]


def get_recent_entries(days: int = 7) -> list[JournalEntry]:
    """Return entries from the past *days* days."""
    since = (date.today() - timedelta(days=days)).isoformat()
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM journal_entries WHERE date >= ? ORDER BY date DESC",
        (since,),
    ).fetchall()
    return [_row_to_entry(r) for r in rows]
