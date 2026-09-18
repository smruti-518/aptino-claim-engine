from fastapi import FastAPI
from pydantic import ValidationError

from src.claim_engine.agents.models import ClaimInput
from src.claim_engine.agents.decision_engine import ClaimDecisionEngine


app = FastAPI(
    title="Aptino Claim Decision Engine",
    version="0.1.0",
)

engine = ClaimDecisionEngine()


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "aptino-claim-engine",
    }

@app.get("/")
def root():
    return {
        "service": "aptino-claim-engine",
        "status": "running",
        "docs": "/docs"
    }

@app.post("/analyze")
def analyze_claim(claim: ClaimInput):
    return engine.analyze(claim).model_dump()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.claim_engine.api.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )