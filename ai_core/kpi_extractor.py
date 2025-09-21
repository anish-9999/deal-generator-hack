from __future__ import annotations
import json
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
from typing import List, Dict, Any
from .schemas import KPIItem
# from .safety import default_safety
from .config import PROJECT_ID, LOCATION, GEMINI_MODEL
from .prompts import EXTRACTION_SYSTEM, EXTRACTION_USER_TEMPLATE

class KPIExtractor:
    def __init__(self):
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        self.model = GenerativeModel(GEMINI_MODEL)

    def extract(self, contexts: List[Dict[str, Any]]) -> List[KPIItem]:
        """
        contexts: list of {"text": "...", "meta": {...}}
        """
        # Concatenate top contexts (truncate if huge)
        blocks = []
        for i, c in enumerate(contexts):
            meta = c.get("meta", {})
            p = meta.get("page") or meta.get("slide")
            prefix = f"[Chunk {i+1} | page/slide={p}]"
            blocks.append(prefix + "\n" + c["text"])
        joined = "\n\n".join(blocks)[:30000]

        user_prompt = EXTRACTION_USER_TEMPLATE.format(context=joined)
        cfg = GenerationConfig(
            temperature=0.2,
            response_mime_type="application/json",
            max_output_tokens=2048,
        )
        resp = self.model.generate_content(
            [EXTRACTION_SYSTEM, user_prompt],
            generation_config=cfg,
            # safety_settings=default_safety()
        )
        txt = resp.text or "{}"
        try:
            data = json.loads(txt)
            items = data.get("metrics", [])
        except Exception:
            items = []
        # Validate & coerce
        out: List[KPIItem] = []
        for it in items:
            try:
                out.append(KPIItem(**it))
            except Exception:
                # ignore malformed items
                pass
        return out
