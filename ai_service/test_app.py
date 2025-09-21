from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="AI Test Service", version="1.0")

class StartupMeta(BaseModel):
    name: str
    sector: str
    stage: str
    country: Optional[str] = None

class Weights(BaseModel):
    Team: int = 25
    Market: int = 25
    Product: int = 20
    Traction: int = 20
    Moat: int = 10

class GenerateRequest(BaseModel):
    gcs_paths: List[str]
    startup: StartupMeta
    weights: Optional[Weights] = None

class DealNote(BaseModel):
    summary: str = "This is a test deal note generated for testing purposes."
    score: int = 85
    recommendation: str = "INVEST"

@app.get("/")
def root():
    return {"message": "AI Test Service is running"}

@app.post("/v1/deal-notes/generate", response_model=DealNote)
def generate_deal_note(req: GenerateRequest):
    # Simulate deal note generation
    deal_note = DealNote(
        summary=f"Generated deal note for {req.startup.name} in {req.startup.sector} sector. "
                f"Analyzed {len(req.gcs_paths)} files. "
                f"Weights: Team({req.weights.Team if req.weights else 25}%), "
                f"Market({req.weights.Market if req.weights else 25}%), "
                f"Product({req.weights.Product if req.weights else 20}%), "
                f"Traction({req.weights.Traction if req.weights else 20}%), "
                f"Moat({req.weights.Moat if req.weights else 10}%)",
        score=85,
        recommendation="INVEST"
    )
    return deal_note