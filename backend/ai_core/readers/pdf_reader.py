from __future__ import annotations
import fitz  # PyMuPDF
from typing import Tuple, List, Dict, Any, Optional
from ..config import ENABLE_VISION_OCR

# Optional OCR for scanned PDFs
def _vision_ocr_pdf(gcs_uri_or_path: str) -> str:
    """
    OPTIONAL: If you deploy in GCP and want OCR for scanned PDFs, wire Cloud Vision here.
    Vision supports asynchronous PDF/TIFF OCR from GCS buckets producing JSON results.
    Docs: https://cloud.google.com/vision/docs/pdf
    """
    # Placeholder for your Vision client call if you enable OCR.
    # For now, return empty and rely on text extraction.
    return ""

def read_pdf(path: str, doc_id: Optional[str] = None) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Extracts text from a PDF using PyMuPDF. If text is empty and OCR is enabled,
    you can integrate Vision OCR fallback by calling _vision_ocr_pdf.
    Returns (full_text, page_spans) where page_spans contains page-wise info for evidence mapping.
    """
    doc = fitz.open(path)
    texts = []
    spans = []
    for i, page in enumerate(doc):
        t = page.get_text("text")
        texts.append(t)
        spans.append({"doc_id": doc_id or path, "page": i+1, "char_count": len(t)})
    full_text = "\n".join(texts)

    if ENABLE_VISION_OCR and len(full_text.strip()) == 0:
        # Wire your OCR fallback only if needed
        full_text = _vision_ocr_pdf(path)

    return full_text, spans
