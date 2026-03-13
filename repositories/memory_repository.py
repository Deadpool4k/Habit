"""Repository for AI message history and long-term memory."""
from database.database import get_connection
from models.ai_memory import AIMemory


def add_message(role: str, content: str) -> None:
    """Append a chat message to the persistent history."""
    conn = get_connection()
    conn.execute(
        "INSERT INTO ai_messages (role, content) VALUES (?, ?)", (role, content)
    )
    conn.commit()


def get_all_messages(limit: int = 100) -> list[dict]:
    """Return up to *limit* messages ordered oldest-first."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT role, content, created_at FROM ai_messages ORDER BY id DESC LIMIT ?",
        (limit,),
    ).fetchall()
    return [{"role": r["role"], "content": r["content"], "created_at": r["created_at"]}
            for r in reversed(rows)]


def clear_messages() -> None:
    """Delete all stored chat messages."""
    conn = get_connection()
    conn.execute("DELETE FROM ai_messages")
    conn.commit()


def add_memory(memory_type: str, content: str, embedding: str = "") -> int:
    """Insert a new memory entry and return its id."""
    conn = get_connection()
    cur = conn.execute(
        """INSERT INTO ai_memory (memory_type, content, embedding)
           VALUES (?, ?, ?)""",
        (memory_type, content, embedding),
    )
    conn.commit()
    return cur.lastrowid


def get_memories_by_type(memory_type: str) -> list[AIMemory]:
    """Return all memories of a given type."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM ai_memory WHERE memory_type = ? ORDER BY id DESC",
        (memory_type,),
    ).fetchall()
    return [_row_to_memory(r) for r in rows]


def get_all_memories() -> list[AIMemory]:
    """Return all stored memories."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM ai_memory ORDER BY id DESC"
    ).fetchall()
    return [_row_to_memory(r) for r in rows]


def update_memory(memory_id: int, content: str, embedding: str = "") -> None:
    """Update an existing memory's content and embedding."""
    conn = get_connection()
    conn.execute(
        """UPDATE ai_memory
           SET content=?, embedding=?, updated_at=datetime('now')
           WHERE id=?""",
        (content, embedding, memory_id),
    )
    conn.commit()


def delete_memory(memory_id: int) -> None:
    """Delete a memory entry by id."""
    conn = get_connection()
    conn.execute("DELETE FROM ai_memory WHERE id = ?", (memory_id,))
    conn.commit()


def _row_to_memory(row) -> AIMemory:
    return AIMemory(
        id=row["id"],
        memory_type=row["memory_type"],
        content=row["content"],
        embedding=row["embedding"] or "",
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )
