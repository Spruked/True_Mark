from fastapi import UploadFile, File, Form, BackgroundTasks, Body, Depends
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil
import os
import uuid
import zipfile
from typing import Any, Dict, List
import time
import datetime
import hashlib

try:
    from .main import app
    from .auth import authenticate_admin, require_admin_session
    from .pricing import calculate_quote, load_pricing, save_pricing
except ImportError:
    from main import app
    from auth import authenticate_admin, require_admin_session
    from pricing import calculate_quote, load_pricing, save_pricing

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Vault structure for persistent records
VAULT_DIR = "vault"
os.makedirs(VAULT_DIR, exist_ok=True)
NFT_LOG = []
USER_LOG = []
SERIAL_COUNTER = 1

class MintRequest(BaseModel):
    name: str
    email: str
    nft_type: str
    file_size_gb: float
    metadata: dict


class QuoteRequest(BaseModel):
    nft_type: str
    package_tier: str = "starter"
    encryption: str = "none"
    chain: str = "polygon"
    quantity: int = 1
    estimated_storage_gb: float = 0.0


class AdminLoginRequest(BaseModel):
    email: str
    password: str

@app.post("/mint")
def mint_nft(
    background_tasks: BackgroundTasks,
    name: str = Form(...),
    email: str = Form(...),
    nft_type: str = Form(...),
    file: UploadFile = File(...),
    metadata: str = Form(...),
    package_tier: str = Form("starter"),
    encryption: str = Form("none"),
    chain: str = Form("polygon"),
    quantity: int = Form(1)
):
    global SERIAL_COUNTER
    # Assign serial number
    serial = f"TM-{SERIAL_COUNTER:05d}"
    SERIAL_COUNTER += 1
    # Save file temporarily
    temp_dir = f"temp/{uuid.uuid4()}"
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    # Timestamps
    epoch_time = int(time.time())
    standard_time = datetime.datetime.utcnow().isoformat() + "Z"
    julian_time = datetime.datetime.utcnow().toordinal() + 1721424.5 + (datetime.datetime.utcnow().hour/24) + (datetime.datetime.utcnow().minute/1440) + (datetime.datetime.utcnow().second/86400)
    # Glyph trace (SHA-256 of serial + filename + metadata)
    glyph_input = f"{serial}|{file.filename}|{metadata}"
    glyph_trace = hashlib.sha256(glyph_input.encode()).hexdigest()
    nft_record = {
        "serial": serial,
        "nft_type": nft_type,
        "package_tier": package_tier,
        "encryption": encryption,
        "chain": chain,
        "quantity": quantity,
        "filename": file.filename,
        "metadata": metadata,
        "epoch": epoch_time,
        "standard": standard_time,
        "julian": julian_time,
        "glyph": glyph_trace
    }
    NFT_LOG.append(nft_record)
    # Persist in vault
    with open(os.path.join(VAULT_DIR, f"{serial}.json"), "w") as f:
        import json
        json.dump(nft_record, f, indent=2)
    # Log user session (for admin, not persistent)
    USER_LOG.append({
        "name": name,
        "email": email,
        "serial": serial
    })
    # Zip user data for download
    zip_path = os.path.join(temp_dir, f"truemark_{serial}_data.zip")
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        zipf.write(file_path, arcname=file.filename)
    # Schedule cleanup
    background_tasks.add_task(shutil.rmtree, temp_dir)
    return FileResponse(zip_path, filename=f"truemark_{serial}_data.zip")

@app.post("/admin/login")
def admin_login(credentials: AdminLoginRequest):
    return authenticate_admin(credentials.email, credentials.password)

@app.get("/admin/session")
def get_admin_session(session: Dict[str, Any] = Depends(require_admin_session)):
    return {
        "email": session["sub"],
        "expires_at": session["exp"],
    }

@app.get("/admin/nfts")
def get_nft_log(session: Dict[str, Any] = Depends(require_admin_session)):
    return JSONResponse(content=NFT_LOG)

@app.get("/admin/users")
def get_user_log(session: Dict[str, Any] = Depends(require_admin_session)):
    return JSONResponse(content=USER_LOG)

@app.get("/admin/pricing")
def get_pricing(session: Dict[str, Any] = Depends(require_admin_session)):
    return JSONResponse(content=load_pricing())


@app.put("/admin/pricing")
def update_pricing(
    updates: Dict[str, Any] = Body(...),
    session: Dict[str, Any] = Depends(require_admin_session),
):
    return JSONResponse(content=save_pricing(updates))


@app.get("/pricing")
def get_public_pricing():
    return JSONResponse(content=load_pricing())


@app.post("/quote")
def get_quote(quote_request: QuoteRequest):
    try:
        return JSONResponse(content=calculate_quote(quote_request.dict()))
    except ValueError as error:
        return JSONResponse(content={"error": str(error)}, status_code=400)

@app.get("/serial/next")
def get_public_next_serial():
    return {"next_serial": f"TM-{SERIAL_COUNTER:05d}"}

@app.get("/admin/serial")
def get_next_serial(session: Dict[str, Any] = Depends(require_admin_session)):
    return {"next_serial": f"TM-{SERIAL_COUNTER:05d}"}
