from fastapi import FastAPI
from pydantic import BaseModel, model_validator
from typing import List, Optional
import time
import os

app = FastAPI(title="Mock AI Service", version="1.0")

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

    @model_validator(mode='after')
    def validate_sum(self):
        total = self.Team + self.Market + self.Product + self.Traction + self.Moat
        if total != 100:
            raise ValueError(f"Weights must sum to 100 (got {total}).")
        return self

class GenerateRequest(BaseModel):
    gcs_paths: List[str]
    startup: StartupMeta
    weights: Optional[Weights] = None

class DealNote(BaseModel):
    summary: str
    score: int
    recommendation: str

@app.get("/")
def root():
    return {"message": "Mock AI Service is running", "status": "healthy"}

@app.post("/v1/deal-notes/generate", response_model=DealNote)
def generate_deal_note(req: GenerateRequest):
    print(f"🔥 Mock AI Service - Received request:")
    print(f"   GCS Paths: {req.gcs_paths}")
    print(f"   Startup: {req.startup.name} ({req.startup.sector})")
    print(f"   Weights: Team={req.weights.Team}, Market={req.weights.Market}, Product={req.weights.Product}, Traction={req.weights.Traction}, Moat={req.weights.Moat}")

    # Simulate processing time
    print("⏳ Processing documents...")
    time.sleep(2)  # Simulate 2 second processing

    # Extract file names for more realistic summary
    file_names = []
    for path in req.gcs_paths:
        if path.startswith("gs://"):
            filename = os.path.basename(path)
            file_names.append(filename)

    # Generate realistic deal note based on weights
    dominant_factor = max(
        ("Team", req.weights.Team),
        ("Market", req.weights.Market),
        ("Product", req.weights.Product),
        ("Traction", req.weights.Traction),
        ("Moat", req.weights.Moat)
    )

    score = 75 + (req.weights.Team // 5) + (req.weights.Market // 5)  # Dynamic scoring

    recommendation = "STRONG INVEST" if score >= 85 else "INVEST" if score >= 75 else "CONSIDER"

    deal_note = DealNote(
        summary=f"**Investment Analysis for {req.startup.name}**\n\n"
                f"**Company Overview:** {req.startup.name} is a {req.startup.stage}-stage company operating in the {req.startup.sector} sector"
                f"{f' based in {req.startup.country}' if req.startup.country else ''}.\n\n"
                f"**Document Analysis:** Reviewed {len(req.gcs_paths)} document(s) including {', '.join(file_names[:2])}{'...' if len(file_names) > 2 else ''}.\n\n"
                f"**Investment Thesis:** Based on the weighted analysis (emphasizing {dominant_factor[0].lower()} at {dominant_factor[1]}%), "
                f"the company demonstrates strong fundamentals. Key strengths include experienced founding team, "
                f"large addressable market opportunity, compelling product-market fit, and promising early traction metrics.\n\n"
                f"**Key Highlights:**\n"
                f"• Strong team with domain expertise\n"
                f"• Clear market opportunity and positioning\n"
                f"• Product demonstrates competitive advantages\n"
                f"• Early customer validation and growth signals\n"
                f"• Defensible business model and moat\n\n"
                f"**Risk Factors:** Standard early-stage risks including execution, market adoption, and competitive landscape.\n\n"
                f"**Investment Recommendation:** {recommendation} based on comprehensive analysis.",
        score=score,
        recommendation=recommendation
    )

    print(f"✅ Generated deal note: {deal_note.recommendation} (Score: {deal_note.score})")
    return deal_note

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)