from __future__ import annotations
from typing import List, Dict
from .config import CHUNK_SIZE, CHUNK_OVERLAP

def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[Dict]:
    """
    Simple character-based chunker (safe for mixed languages). For production,
    you may move to a token-aware splitter.
    """
    chunks = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + size, n)
        chunk = text[start:end]
        chunks.append({"text": chunk, "start": start, "end": end})
        if end == n:
            break
        start = end - overlap
        if start < 0: start = 0
    return chunks
