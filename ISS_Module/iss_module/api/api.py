"""Minimal FastAPI interface for ISS timekeeping."""

from pathlib import Path

from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from ..core.ISS import ISS
from ..core.utils import ISS_REFERENCE_FRAME, canonical_timestamp, current_timecodes, format_iss_time, format_timestamp
from ..session_store import current_session, end_session, list_sessions, start_session
from pydantic import BaseModel


app = FastAPI(
    title="ISS Timekeeping API",
    description="Standalone time representations and time-anchor data.",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    # The Tauri webview sends a CORS preflight before mission POSTs.
    # This API is bound to loopback, so the local widget does not need
    # credentialed cross-origin cookies or browser credentials.
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

iss_instance = ISS()
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))


class MissionStartRequest(BaseModel):
    label: str = "Work Session"


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(request=request, name="dashboard.html", context={})


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse(request=request, name="dashboard.html", context={})


@app.get("/api/health")
async def health():
    timecodes = current_timecodes()
    return {
        "status": "healthy" if iss_instance.heartbeat() else "unhealthy",
        "timestamp": timecodes["iso_timestamp"],
        "stardate": timecodes["stardate"],
    }


@app.get("/api/status")
async def status():
    return iss_instance.get_status()


@app.get("/api/time")
async def time_formats(reference_frame: str = Query(ISS_REFERENCE_FRAME, min_length=1, max_length=120)):
    """Return the canonical timestamp and its four time concepts."""
    timecodes = current_timecodes()
    timecodes["reference_frame"] = reference_frame
    canonical = canonical_timestamp(_timecodes=timecodes)
    mission = current_session()
    if mission:
        canonical = canonical_timestamp(
            mission_epoch_ns=mission["started_iss_time_ns"],
            reference_frame=reference_frame,
            _timecodes=timecodes,
        )
    return {
        "iss_time_ns": canonical["iss_time_ns"],
        "scale_name": canonical["scale_name"],
        "scale_designation": canonical["scale_designation"],
        "epoch_label": canonical["epoch"],
        "reference_frame": canonical["reference_frame"],
        "universal_coordinate_time": canonical["iss_time_ns"],
        "epoch": canonical["epoch_timestamp_ns"],
        "standard": canonical["standard_timestamp"],
        "julian": f"JD {canonical['julian_timestamp']:.9f}",
        "iss": canonical["iss_timestamp"],
        "proper_time_ns": canonical["proper_time_ns"],
        "mission_elapsed_ns": canonical["mission_elapsed_ns"],
        "local_display_time": canonical["local_display_time"],
        "human_iss": canonical["human_display"],
        "human_iss_precise": canonical["human_display_precise"],
        "human_iss_short": format_iss_time(canonical["iss_time_ns"], precision="seconds").rsplit(" ", 1)[0],
        "iso": timecodes["iso_timestamp"],
        "stardate": f"Stardate {canonical['stardate']:.9f}",
        "julian_display": format_timestamp(format_type="julian"),
        "human": format_timestamp(format_type="human"),
        "unix": timecodes["unix_timestamp"],
        "tai_utc_offset_ns": timecodes["tai_utc_offset_ns"],
        "mission": mission,
        "anchor_hash": timecodes["anchor_hash"],
    }


@app.post("/api/mission/start")
async def mission_start(request: MissionStartRequest):
    try:
        return start_session(request.label)
    except ValueError as error:
        from fastapi import HTTPException
        raise HTTPException(status_code=409, detail=str(error)) from error


@app.post("/api/mission/end")
async def mission_end():
    try:
        return end_session()
    except ValueError as error:
        from fastapi import HTTPException
        raise HTTPException(status_code=409, detail=str(error)) from error


@app.get("/api/mission/current")
async def mission_current():
    return {"active": current_session()}


@app.get("/api/mission/sessions")
async def mission_sessions(limit: int = Query(100, ge=1, le=1000)):
    return {"sessions": list_sessions(limit)}


@app.get("/api/stardate")
async def stardate():
    timecodes = current_timecodes()
    return {
        "stardate": timecodes["stardate"],
        "human_iss": format_iss_time(timecodes["iss_time_ns"]),
        "iss_time_ns": timecodes["iss_time_ns"],
        "scale": timecodes["scale_designation"],
    }
