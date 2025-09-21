from __future__ import annotations
import os

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("PROJECT_ID") or ""
LOCATION = os.getenv("VERTEXAI_LOCATION", "us-central1")

# Gemini + Embeddings
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")  # price/perf
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-004")

# Chunking
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1100"))   # characters
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "180"))

# OCR toggle (only needed if you expect scanned PDFs)
ENABLE_VISION_OCR = os.getenv("ENABLE_VISION_OCR", "false").lower() == "true"

# Default scoring weights (can be overridden per request)
DEFAULT_WEIGHTS = {
    "Team": 25,
    "Market": 25,
    "Product": 20,
    "Traction": 20,
    "Moat": 10,
}
