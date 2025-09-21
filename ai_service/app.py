from __future__ import annotations

import os
import re
from typing import List, Dict, Optional
from typing_extensions import Annotated

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Set Google Cloud project explicitly
os.environ.setdefault('GOOGLE_CLOUD_PROJECT', 'hack-deal-generator')

from ai_core.deal_note_generator import generate_deal_note
from ai_service.gcs_io import download_gcs_objects
import asyncio
import time

# ─────────────────────────────────────────────────────────────
# Request models (typed, validated, with examples)
# ─────────────────────────────────────────────────────────────

class StartupMeta(BaseModel):
    """Explicit, documented startup metadata."""
    name: str = Field(..., description="Startup name")
    sector: str = Field(..., description="Sector (e.g., SaaS, Fintech, Consumer, Deeptech)")
    stage: str = Field(..., description="Fundraising stage (e.g., Pre-seed, Seed, A, B)")
    country: Optional[str] = Field(None, description="HQ country code or name")

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"name": "Datastride", "sector": "SaaS", "stage": "Seed", "country": "IN"}
            ]
        }
    )

class Weights(BaseModel):
    """Investor weightages for scoring pillars (must sum to 100)."""
    Team: int = 25
    Market: int = 25
    Product: int = 20
    Traction: int = 20
    Moat: int = 10

    @field_validator("Team", "Market", "Product", "Traction", "Moat")
    @classmethod
    def each_between_0_100(cls, v):
        if v < 0 or v > 100:
            raise ValueError("Each weight must be between 0 and 100.")
        return v

    @model_validator(mode='after')
    def validate_sum(self):
        total = self.Team + self.Market + self.Product + self.Traction + self.Moat
        if total != 100:
            raise ValueError(f"Weights must sum to 100 (got {total}).")
        return self

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"Team":25,"Market":25,"Product":20,"Traction":20,"Moat":10},
                {"Team":20,"Market":30,"Product":20,"Traction":20,"Moat":10}
            ]
        }
    )

# Accept only gs://... style URIs
GsUri = Annotated[str, Field(pattern=r"^gs://[a-z0-9.\-_]+/.+",
                             description="GCS URI like gs://bucket/path/file.pdf")]

class GenerateRequest(BaseModel):
    gcs_paths: List[GsUri] = Field(..., min_items=1, description="One or more GCS URIs to PDF/PPT(X)")
    startup: StartupMeta
    weights: Optional[Weights] = None

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "gcs_paths": ["gs://ai-analyst-uploads/decks/sample_pdf.pdf"],
                    "startup": {"name":"Datastride","sector":"SaaS","stage":"Seed","country":"IN"},
                    "weights": {"Team":25,"Market":25,"Product":20,"Traction":20,"Moat":10}
                }
            ]
        }
    )

# ─────────────────────────────────────────────────────────────
# FastAPI app and route
# ─────────────────────────────────────────────────────────────

app = FastAPI(
    title="AI Analyst Service",
    version="1.0",
    description="Upload references to pitch decks in GCS and generate investor-ready Deal Notes."
)

# If ai_core.schemas.DealNote is available, you can show the response schema too:
try:
    from ai_core.schemas import DealNote
    RESPONSE_MODEL = DealNote
except Exception:
    RESPONSE_MODEL = Dict  # fallback if DealNote import fails in your local env

@app.post(
    "/v1/deal-notes/generate",
    summary="Generate a Deal Note from GCS files",
    response_model=RESPONSE_MODEL,  # shows your DealNote structure in Swagger
    tags=["deal-notes"]
)
def generate(req: GenerateRequest):
    try:
        local_files = download_gcs_objects(req.gcs_paths)
        # Optional: reject legacy .ppt (recommend .pptx or PDF)
        # for lf in local_files:
        #     if lf["type"] == "ppt":
        #         raise HTTPException(status_code=400, detail="Upload .pptx or PDF.")

        note = generate_deal_note(
            files=local_files,
            startup_meta=req.startup.model_dump(),
            weights=req.weights.model_dump() if req.weights else None
        )
        return note
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))