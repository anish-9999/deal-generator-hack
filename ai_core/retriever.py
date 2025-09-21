from __future__ import annotations
import numpy as np
from typing import List, Dict, Any
from scipy.spatial.distance import cdist
from .embedder import VertexEmbedder

class SimpleVectorStore:
    """
    Request-scoped in-memory vector store (embeddings live per request).
    For production persistence / multi-user search, move to BigQuery Vector Search or a vector DB.
    """
    def __init__(self):
        self._embedder = VertexEmbedder()
        self._embeddings = None  # (N, D)
        self._metas: List[Dict[str, Any]] = []
        self._texts: List[str] = []

    def add_texts(self, texts: List[str], metas: List[Dict[str, Any]]):
        embs = self._embedder.embed(texts)
        embs = np.array(embs, dtype=np.float32)
        if self._embeddings is None:
            self._embeddings = embs
        else:
            self._embeddings = np.vstack([self._embeddings, embs])
        self._texts.extend(texts)
        self._metas.extend(metas)

    def search(self, query: str, top_k: int = 8) -> List[Dict[str, Any]]:
        q_emb = np.array(self._embedder.embed([query])[0], dtype=np.float32).reshape(1, -1)
        dists = cdist(q_emb, self._embeddings, metric="cosine")[0]  # smaller is closer
        idxs = np.argsort(dists)[:top_k]
        results = []
        for i in idxs:
            results.append({
                "text": self._texts[i],
                "meta": self._metas[i],
                "distance": float(dists[i]),
            })
        return results
