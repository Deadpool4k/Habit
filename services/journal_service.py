"""Business logic for journal entries."""
from datetime import date
from typing import Optional

from models.journal_entry import JournalEntry
import repositories.journal_repository as repo


def get_or_create_entry(entry_date: Optional[str] = None) -> JournalEntry:
    """Return existing journal entry for *entry_date*, or a new blank one."""
    if entry_date is None:
        entry_date = date.today().isoformat()
    existing = repo.get_entry_by_date(entry_date)
    if existing:
        return existing
    return JournalEntry(date=entry_date)


def save_entry(entry: JournalEntry) -> JournalEntry:
    """Persist a journal entry and return the saved copy."""
    return repo.create_or_update_entry(entry)


def get_recent_entries(days: int = 7) -> list[JournalEntry]:
    """Return journal entries from the last *days* days."""
    return repo.get_recent_entries(days)
