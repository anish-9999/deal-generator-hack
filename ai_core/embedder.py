from __future__ import annotations
import vertexai
from vertexai.language_models import TextEmbeddingModel
from typing import List, Dict
import hashlib
import time
import logging
from .config import PROJECT_ID, LOCATION, EMBEDDING_MODEL

# In-memory cache for embeddings (in production, use Redis or persistent cache)
_embedding_cache: Dict[str, List[float]] = {}
_last_request_time = 0
_request_count = 0

class VertexEmbedder:
    def __init__(self):
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        self.model = TextEmbeddingModel.from_pretrained(EMBEDDING_MODEL)
        self.logger = logging.getLogger(__name__)

    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    def _rate_limit(self):
        """Simple rate limiting: max 4 requests per minute to stay under quota"""
        global _last_request_time, _request_count
        current_time = time.time()

        # Reset counter every minute
        if current_time - _last_request_time > 60:
            _request_count = 0
            _last_request_time = current_time

        # If we've made 4 requests in the current minute, wait
        if _request_count >= 4:
            wait_time = 60 - (current_time - _last_request_time)
            if wait_time > 0:
                self.logger.info(f"Rate limiting: waiting {wait_time:.1f} seconds")
                time.sleep(wait_time)
                _request_count = 0
                _last_request_time = time.time()

        _request_count += 1

    def embed(self, texts: List[str]) -> List[List[float]]:
        """
        Embed texts with caching and rate limiting
        """
        if not texts:
            return []

        # Check cache first
        cached_results = []
        uncached_texts = []
        uncached_indices = []

        for i, text in enumerate(texts):
            cache_key = self._get_cache_key(text)
            if cache_key in _embedding_cache:
                cached_results.append((i, _embedding_cache[cache_key]))
            else:
                uncached_texts.append(text)
                uncached_indices.append(i)

        self.logger.info(f"Cache hit: {len(cached_results)}/{len(texts)} embeddings")

        # If all texts are cached, return cached results
        if not uncached_texts:
            result = [None] * len(texts)
            for i, embedding in cached_results:
                result[i] = embedding
            return result

        # Rate limit before making API call
        self._rate_limit()

        # Batch embed uncached texts (max 5 at a time to avoid quota issues)
        batch_size = min(5, len(uncached_texts))
        uncached_embeddings = []

        for i in range(0, len(uncached_texts), batch_size):
            batch = uncached_texts[i:i + batch_size]
            self.logger.info(f"Embedding batch of {len(batch)} texts")

            try:
                batch_embeddings = [e.values for e in self.model.get_embeddings(batch)]
                uncached_embeddings.extend(batch_embeddings)

                # Cache the results
                for j, text in enumerate(batch):
                    cache_key = self._get_cache_key(text)
                    _embedding_cache[cache_key] = batch_embeddings[j]

            except Exception as e:
                self.logger.error(f"Embedding failed for batch: {e}")
                # Return zero vectors as fallback
                uncached_embeddings.extend([[0.0] * 768] * len(batch))

        # Combine cached and uncached results
        result = [None] * len(texts)

        # Fill in cached results
        for i, embedding in cached_results:
            result[i] = embedding

        # Fill in uncached results
        for i, embedding in zip(uncached_indices, uncached_embeddings):
            result[i] = embedding

        return result
