"""Lightweight keyword-based similarity search (no external embedding API)."""
import math
import re
from collections import Counter


def _tokenize(text: str) -> list[str]:
    """Lowercase and split text into word tokens."""
    return re.findall(r"[a-z0-9]+", text.lower())


def simple_similarity(query: str, text: str) -> float:
    """Compute a cosine-like TF overlap score between query and text.

    Returns a float in [0, 1] — higher means more relevant.
    """
    query_tokens = _tokenize(query)
    text_tokens = _tokenize(text)
    if not query_tokens or not text_tokens:
        return 0.0

    query_counts = Counter(query_tokens)
    text_counts = Counter(text_tokens)

    # Dot product over shared terms
    shared_keys = set(query_counts.keys()) & set(text_counts.keys())
    dot = sum(query_counts[k] * text_counts[k] for k in shared_keys)
    if dot == 0:
        return 0.0

    query_norm = math.sqrt(sum(v * v for v in query_counts.values()))
    text_norm = math.sqrt(sum(v * v for v in text_counts.values()))
    if query_norm == 0 or text_norm == 0:
        return 0.0

    return dot / (query_norm * text_norm)


def find_relevant_memories(query: str, memories: list, top_k: int = 5) -> list:
    """Return the top-k most relevant memory objects from *memories*.

    Each item in *memories* is expected to have a `content` attribute.
    """
    scored = [
        (simple_similarity(query, m.content), m)
        for m in memories
    ]
    scored.sort(key=lambda x: x[0], reverse=True)
    return [m for _, m in scored[:top_k]]
