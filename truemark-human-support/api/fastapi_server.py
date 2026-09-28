"""Human Support escalation service boundary."""

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="True Mark Human Support Escalation Service")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3300", "http://127.0.0.1:3300"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
CASES: dict[str, dict[str, Any]] = {}


class EscalationRequest(BaseModel):
    reason_code: str = "CUSTOMER_REQUESTED_HUMAN"
    account_id: str
    object_id: str | None = None
    authorized_context: dict[str, Any] = Field(default_factory=dict)


class MessageRequest(BaseModel):
    message: str
    reason_code: str | None = None


@app.post("/api/escalations")
async def create_escalation(request: EscalationRequest):
    case_id = f"CASE-TM-{uuid4().hex[:12].upper()}"
    CASES[case_id] = {"case_id": case_id, "account_id": request.account_id, "object_id": request.object_id, "reason_code": request.reason_code, "authorized_context": request.authorized_context, "status": "WAITING_FOR_AGENT", "created_at": datetime.now(timezone.utc).isoformat(), "messages": []}
    return {"case_id": case_id, "status": "WAITING_FOR_AGENT"}


@app.get("/api/escalations/{case_id}")
async def get_escalation(case_id: str):
    case = CASES.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Escalation case not found.")
    return {key: value for key, value in case.items() if key != "messages"}


@app.post("/api/escalations/{case_id}/messages")
async def queue_message(case_id: str, request: MessageRequest):
    case = CASES.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Escalation case not found.")
    if case["status"] in {"RESOLVED", "CLOSED"}:
        raise HTTPException(status_code=409, detail="This escalation case is closed.")
    case["messages"].append({"from": "customer", "message": request.message, "created_at": datetime.now(timezone.utc).isoformat()})
    return {"status": "QUEUED_FOR_HUMAN_AGENT"}


@app.post("/api/escalations/{case_id}/close")
async def close_escalation(case_id: str):
    case = CASES.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Escalation case not found.")
    case["status"] = "CLOSED"
    return {"case_id": case_id, "status": case["status"]}
