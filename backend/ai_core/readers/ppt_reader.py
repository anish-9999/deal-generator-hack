from __future__ import annotations
from typing import Tuple, List, Dict, Any, Optional
from pptx import Presentation

def read_ppt(path: str, doc_id: Optional[str] = None) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Extract text from PPT/PPTX slides (text-based content).
    If slides are images, consider exporting to PDF and using OCR as a fallback.
    """
    prs = Presentation(path)
    parts = []
    spans = []
    for i, slide in enumerate(prs.slides):
        texts = []
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                txt = (shape.text or "").strip()
                if txt:
                    texts.append(txt)
        block = "\n".join(texts)
        parts.append(block)
        spans.append({"doc_id": doc_id or path, "slide": i+1, "char_count": len(block)})
    return "\n\n".join(parts), spans
