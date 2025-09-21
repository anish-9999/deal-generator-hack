from __future__ import annotations
import os, json, datetime as dt
from typing import Dict, Any, List, Tuple
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
from .config import PROJECT_ID, LOCATION, GEMINI_MODEL, DEFAULT_WEIGHTS
from .schemas import DealNote, KPIItem, PillarScores, Recommendation
from .readers.pdf_reader import read_pdf
from .readers.ppt_reader import read_ppt
from .chunker import chunk_text
from .retriever import SimpleVectorStore
from .kpi_extractor import KPIExtractor
from .prompts import SYNTH_SYSTEM, SYNTH_USER_TEMPLATE
# from .safety import default_safety

# --- Helper scoring (simple baseline; tune as you collect data) ----
def compute_pillars(kpis: List[KPIItem]) -> PillarScores:
    """
    Very simple placeholder logic: map presence of solid KPIs to pillar points.
    Replace with your real benchmark-based scoring when available.
    """
    name_map = {k.name.lower(): k for k in kpis}
    # Example heuristics:
    traction = 50.0
    if "arr" in name_map and (name_map["arr"].value or 0) > 0:
        traction += 20
    if "growth_pct" in name_map and (name_map["growth_pct"].value or 0) >= 50:
        traction += 15
    if "ndr" in name_map and (name_map["ndr"].value or 0) >= 110:
        traction += 10
    traction = min(100.0, traction)

    product = 60.0  # placeholder
    market = 60.0   # placeholder
    team = 60.0     # placeholder
    moat = 50.0     # placeholder

    return PillarScores(Team=team, Market=market, Product=product, Traction=traction, Moat=moat)

def weighted_overall(pillars: PillarScores, weights: Dict[str, int]) -> float:
    wsum = sum(weights.values()) or 1
    total = (
        pillars.Team * weights.get("Team", 0)
        + pillars.Market * weights.get("Market", 0)
        + pillars.Product * weights.get("Product", 0)
        + pillars.Traction * weights.get("Traction", 0)
        + pillars.Moat * weights.get("Moat", 0)
    ) / wsum
    return round(total, 1)

def classify_recommendation(score: float) -> Recommendation:
    if score >= 80:
        return Recommendation(label="Invest", confidence=0.8, rationale="Strong overall score.")
    if score >= 60:
        return Recommendation(label="Watch", confidence=0.65, rationale="Mixed signals; monitor traction and risks.")
    return Recommendation(label="Pass", confidence=0.7, rationale="Below threshold on multiple pillars.")

# --- Main orchestration -------------------------------------------------------
class DealNoteGenerator:
    def __init__(self):
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        self.model = GenerativeModel(GEMINI_MODEL)
        self.kpi_extractor = KPIExtractor()

    def _load_and_chunk(self, files: List[Dict[str, Any]]) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        files: List[{"path": "/path/to/file.pdf", "type": "pdf"|"ppt"|"pptx", "doc_id": "optional"}]
        Returns (chunks_text, metas)
        """
        big_text = []
        metas = []
        for f in files:
            ftype = f.get("type") or os.path.splitext(f["path"])[1].lower().strip(".")
            doc_id = f.get("doc_id") or f["path"]
            if ftype in ["pdf"]:
                text, spans = read_pdf(f["path"], doc_id=doc_id)
            elif ftype in ["ppt", "pptx"]:
                text, spans = read_ppt(f["path"], doc_id=doc_id)
            else:
                raise ValueError(f"Unsupported type: {ftype}")

            # Chunk the text
            chs = chunk_text(text)
            for ch in chs:
                big_text.append(ch["text"])
                metas.append({"doc_id": doc_id})
        return big_text, metas

    def _build_store(self, chunks: List[str], metas: List[Dict[str, Any]]) -> SimpleVectorStore:
        store = SimpleVectorStore()
        store.add_texts(chunks, metas)
        return store

    def _retrieve_for_topics(self, store: SimpleVectorStore) -> List[Dict[str, Any]]:
        # Compound query to pull coverage for the note
        topics = [
            "company overview, team background, milestones",
            "revenue metrics: ARR, MRR, growth percentage, cohorts, NDR",
            "customer metrics: churn, retention, logos, segments",
            "unit economics: CAC, LTV, gross margin",
            "market size: TAM, SAM, SOM and methodology",
            "product differentiation, moat, IP",
            "key risks: inconsistencies, inflated TAM, unusual churn patterns"
        ]
        results = []
        for t in topics:
            results.extend(store.search(t, top_k=3))
        # Deduplicate by text snippet
        seen = set()
        uniq = []
        for r in results:
            key = r["text"][:80]
            if key not in seen:
                uniq.append(r); seen.add(key)
        return uniq[:20]

    def generate(self,
                 files: List[Dict[str, Any]],
                 startup_meta: Dict[str, Any],
                 weights: Dict[str, int] | None = None,
                 benchmarks: List[Dict[str, Any]] | None = None,
                 risks_known: List[Dict[str, Any]] | None = None) -> DealNote:

        weights = weights or DEFAULT_WEIGHTS
        chunks, metas = self._load_and_chunk(files)
        store = self._build_store(chunks, metas)

        contexts = self._retrieve_for_topics(store)
        # Extract KPIs via Gemini JSON mode
        kpis: List[KPIItem] = self.kpi_extractor.extract(contexts)

        # Compute simple pillar scores and overall with investor weights
        pillars = compute_pillars(kpis)
        overall = weighted_overall(pillars, weights)
        reco = classify_recommendation(overall)

        # Summarize context for synthesis
        summary_ctx = []
        for c in contexts[:10]:
            clean_text = c['text'][:300].replace("\n", " ")
            summary_ctx.append(f"- {clean_text}")
        context_summary = "\n".join(summary_ctx)
        # Prepare synthesis prompt
        kpi_json = json.dumps([k.model_dump() for k in kpis], ensure_ascii=False)
        user_prompt = SYNTH_USER_TEMPLATE.format(
            startup_meta=json.dumps(startup_meta, ensure_ascii=False),
            kpi_json=kpi_json,
            context_summary=context_summary,
            benchmarks=json.dumps(benchmarks or [], ensure_ascii=False),
            risks=json.dumps(risks_known or [], ensure_ascii=False),
            weights=json.dumps(weights)
        )

        cfg = GenerationConfig(temperature=0.2, max_output_tokens=2048)
        resp = self.model.generate_content(
            [SYNTH_SYSTEM, user_prompt],
            generation_config=cfg,
            # safety_settings=default_safety()
        )
        note_md = resp.text or "(No content)"

        # Minimal risk list (add your SQL/LLM rule engine output if available)
        risks = risks_known or []

        # Citations: since we used local RAG over the deck, attach doc_ids for transparency
        citations = [{"doc_id": m.get("doc_id")} for m in metas[:5]]

        note = DealNote(
            startup=startup_meta,
            snapshot={"summary_markdown": note_md.split("\n\n")[0][:800]},
            kpis=kpis,
            risks=risks,
            benchmarks=benchmarks or [],
            scorecard=pillars,
            overall=overall,
            weights=weights,
            recommendation=reco,
            citations=citations,
            generated_at=dt.datetime.utcnow().isoformat() + "Z"
        )
        return note

# Convenience function for your route handler
def generate_deal_note(files: List[Dict[str, Any]],
                       startup_meta: Dict[str, Any],
                       weights: Dict[str, int] | None = None) -> Dict[str, Any]:
    """
    files: [{"path": "...", "type":"pdf|ppt|pptx", "doc_id":"optional"}, ...]
    startup_meta: {"name":"...", "sector":"SaaS", "stage":"Seed", ...}
    """
    gen = DealNoteGenerator()
    note = gen.generate(files=files, startup_meta=startup_meta, weights=weights)
    return note.model_dump()
