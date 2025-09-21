from __future__ import annotations
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any

class EvidenceSpan(BaseModel):
    quote: str
    doc_id: Optional[str] = None
    page: Optional[int] = None
    offset: Optional[int] = None

class KPIItem(BaseModel):
    name: str
    value: Optional[float] = None
    unit: Optional[str] = None       # 'USD_M', 'PCT', etc.
    currency: Optional[str] = None   # 'USD'
    period: Optional[str] = None     # 'FY2025', 'Q2-2025'
    confidence: Optional[float] = None
    evidence: Optional[EvidenceSpan] = None

    @field_validator("confidence")
    @classmethod
    def clamp_confidence(cls, v):
        if v is None: return v
        return max(0.0, min(1.0, v))

class PillarScores(BaseModel):
    Team: float = 0
    Market: float = 0
    Product: float = 0
    Traction: float = 0
    Moat: float = 0

class Recommendation(BaseModel):
    label: str
    confidence: float
    rationale: str

class DealNote(BaseModel):
    startup: Dict[str, Any]
    snapshot: Dict[str, Any]
    kpis: List[KPIItem]
    risks: List[Dict[str, Any]]
    benchmarks: List[Dict[str, Any]]
    scorecard: PillarScores
    overall: float
    weights: Dict[str, int]
    recommendation: Recommendation
    citations: List[Dict[str, Any]]
    generated_at: str
