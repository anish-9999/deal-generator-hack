from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Test AI Service", version="1.0")

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
    gcs_paths: List[str]  # Accept GCS paths like gs://bucket/path
    startup: StartupMeta
    weights: Optional[Weights] = None

class DealNote(BaseModel):
    summary: str
    score: int
    recommendation: str

@app.get("/")
def root():
    return {"message": "Test AI Service is running", "status": "healthy"}

@app.post("/v1/deal-notes/generate", response_model=DealNote)
def generate_deal_note(req: GenerateRequest):
    print(f"🔥 Received request:")
    print(f"   GCS Paths: {req.gcs_paths}")
    print(f"   Startup: {req.startup.name} ({req.startup.sector})")
    print(f"   Weights: {req.weights}")

    # Simulate deal note generation
    deal_note = DealNote(
        summary=f"AI-generated deal note for {req.startup.name} in the {req.startup.sector} sector. "
                f"Analysis based on {len(req.gcs_paths)} document(s). "
                f"Investment evaluation with custom weights: "
                f"Team ({req.weights.Team if req.weights else 25}%), "
                f"Market ({req.weights.Market if req.weights else 25}%), "
                f"Product ({req.weights.Product if req.weights else 20}%), "
                f"Traction ({req.weights.Traction if req.weights else 20}%), "
                f"Moat ({req.weights.Moat if req.weights else 10}%). "
                f"Strong founding team with relevant experience, large addressable market, "
                f"compelling product-market fit, and promising early traction metrics.",
        score=87,
        recommendation="STRONG INVEST"
    )

    print(f"✅ Generated deal note: {deal_note.recommendation} (Score: {deal_note.score})")
    return deal_note

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)