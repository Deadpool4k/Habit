"""Database initialization and connection management for SQLite."""
import sqlite3
import os
import sys

# Allow running from any working directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import load_config

_conn = None


def get_connection() -> sqlite3.Connection:
    """Return a singleton SQLite connection, creating it on first call."""
    global _conn
    if _conn is None:
        config = load_config()
        db_path = config.get("db_path", "habit_tracker.db")
        _conn = sqlite3.connect(db_path, check_same_thread=False)
        _conn.row_factory = sqlite3.Row
        _conn.execute("PRAGMA foreign_keys = ON")
    return _conn


def init_db() -> None:
    """Initialize the database by executing schema.sql."""
    conn = get_connection()
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path, "r") as f:
        schema = f.read()
    conn.executescript(schema)
    conn.commit()
