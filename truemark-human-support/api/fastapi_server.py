"""Deprecated local adapter for the True Mark Human Support boundary.

Production escalation is integrated into the main True Mark backend, where
signed account sessions and persistent storage are available. This companion
process exposes only a health/deprecation response so it cannot be mistaken
for an authoritative or secure escalation service.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI(title="True Mark Human Support Adapter")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3300", "http://127.0.0.1:3300"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "deprecated", "service": "main-backend-human-support"}


@app.api_route("/api/escalations", methods=["GET", "POST"])
@app.api_route("/api/escalations/{case_id}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def deprecated_escalation_endpoint():
    return JSONResponse(
        status_code=410,
        content={"detail": "Human Support is integrated into the main True Mark backend at port 13001."},
    )
