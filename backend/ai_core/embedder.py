from __future__ import annotations
import vertexai
from vertexai.language_models import TextEmbeddingModel
from typing import List
from .config import PROJECT_ID, LOCATION, EMBEDDING_MODEL

class VertexEmbedder:
    def __init__(self):
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        self.model = TextEmbeddingModel.from_pretrained(EMBEDDING_MODEL)

    def embed(self, texts: List[str]) -> List[List[float]]:
        # text-embedding-004 returns 768-d embeddings (subject to change per model version)
        # Docs: https://cloud.google.com/bigquery/docs/vector-index-text-search-tutorial
        return [e.values for e in self.model.get_embeddings(texts)]
