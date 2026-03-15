from __future__ import annotations

import os
import shutil
import uuid
import zipfile
from typing import Any, Dict

from fastapi import BackgroundTasks, Body, Depends, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

try:
    from .auth import authenticate_admin, require_admin_session
    from .main import app
    from .market import get_market_snapshot
    from .pricing import calculate_quote, load_pricing, save_pricing
    from .storage import (
        authenticate_user,
        create_user,
        get_analytics,
        get_next_truemark_serial,
        get_user_by_email,
        list_orders,
        list_users,
        record_order,
    )
    from .tax import load_tax_table, resolve_tax_rate, save_tax_table
except ImportError:
    from auth import authenticate_admin, require_admin_session
    from main import app
    from market import get_market_snapshot
    from pricing import calculate_quote, load_pricing, save_pricing
    from storage import (
        authenticate_user,
        create_user,
        get_analytics,
        get_next_truemark_serial,
        get_user_by_email,
        list_orders,
        list_users,
        record_order,
    )
    from tax import load_tax_table, resolve_tax_rate, save_tax_table


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


VAULT_DIR = "vault"
os.makedirs(VAULT_DIR, exist_ok=True)


class QuoteRequest(BaseModel):
    nft_type: str
    package_tier: str = "starter"
    encryption: str = "none"
    chain: str = "polygon"
    quantity: int = 1
    estimated_storage_gb: float = 0.0
    email: str | None = None


class AdminLoginRequest(BaseModel):
    email: str
    password: str


class AccountSignupRequest(BaseModel):
    name: str
    email: str
    password: str
    address_line1: str = ""
    address_line2: str = ""
    city: str = ""
    state: str = ""
    postal_code: str = ""
    phone: str = ""
    dob: str = ""
    marketing: bool = False


class AccountLoginRequest(BaseModel):
    email: str
    password: str


def build_quote_response(quote_payload: QuoteRequest) -> Dict[str, Any]:
    quote = calculate_quote(quote_payload.dict(exclude_none=True))
    tax_table = load_tax_table()
    user = get_user_by_email(quote_payload.email)
    tax_rate = resolve_tax_rate(user.get("state") if user else None, tax_table)
    estimated_tax = round(quote["total"] * tax_rate, 2)
    grand_total = round(quote["total"] + estimated_tax, 2)

    quote["tax_rate"] = round(tax_rate, 6)
    quote["estimated_tax"] = estimated_tax
    quote["grand_total"] = grand_total
    quote["tax_state"] = user.get("state") if user else ""
    return quote


@app.post("/accounts/signup")
def signup_account(account: AccountSignupRequest):
    try:
        return create_user(account.dict())
    except ValueError as error:
        return JSONResponse(content={"detail": str(error)}, status_code=400)


@app.post("/accounts/login")
def login_account(credentials: AccountLoginRequest):
    try:
        return authenticate_user(credentials.email, credentials.password)
    except ValueError as error:
        return JSONResponse(content={"detail": str(error)}, status_code=401)


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
    quantity: int = Form(1),
    payment_method: str = Form("fiat"),
):
    serial = get_next_truemark_serial()
    temp_dir = f"temp/{uuid.uuid4()}"
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size_gb = os.path.getsize(file_path) / (1024 * 1024 * 1024)
    quote = build_quote_response(
        QuoteRequest(
            nft_type=nft_type,
            package_tier=package_tier,
            encryption=encryption,
            chain=chain,
            quantity=quantity,
            estimated_storage_gb=file_size_gb,
            email=email,
        )
    )

    nft_record = {
        "serial": serial,
        "nft_type": nft_type,
        "package_tier": package_tier,
        "encryption": encryption,
        "chain": chain,
        "quantity": quantity,
        "filename": file.filename,
        "metadata": metadata,
        "subtotal": quote["total"],
        "estimated_tax": quote["estimated_tax"],
        "grand_total": quote["grand_total"],
    }

    user = get_user_by_email(email)
    market_snapshot = get_market_snapshot() if payment_method == "crypto" else None
    crypto_token = None
    crypto_spot_price = None

    if market_snapshot and chain in market_snapshot["assets"]:
        crypto_token = "MATIC" if chain == "polygon" else "ETH"
        crypto_spot_price = market_snapshot["assets"][chain]["usd"]

    with open(os.path.join(VAULT_DIR, f"{serial}.json"), "w", encoding="utf-8") as vault_file:
        import json

        json.dump(nft_record, vault_file, indent=2)

    record_order(
        {
            "serial": serial,
            "user_id": user.get("id") if user else None,
            "user_email": email,
            "user_name": name,
            "nft_type": nft_type,
            "package_tier": package_tier,
            "encryption": encryption,
            "chain": chain,
            "quantity": quantity,
            "file_name": file.filename,
            "estimated_storage_gb": file_size_gb,
            "subtotal_usd": quote["total"],
            "tax_amount_usd": quote["estimated_tax"],
            "processing_fee_usd": quote["processing_fee"],
            "discount_amount_usd": quote["discount_amount"],
            "total_usd": quote["grand_total"],
            "payment_method": payment_method,
            "crypto_token": crypto_token,
            "crypto_spot_price_usd": crypto_spot_price,
            "status": "completed",
        }
    )

    zip_path = os.path.join(temp_dir, f"truemark_{serial}_data.zip")
    with zipfile.ZipFile(zip_path, "w") as archive:
        archive.write(file_path, arcname=file.filename)

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


@app.get("/admin/orders")
def get_admin_orders(session: Dict[str, Any] = Depends(require_admin_session)):
    return JSONResponse(content=list_orders())


@app.get("/admin/nfts")
def get_nft_log(session: Dict[str, Any] = Depends(require_admin_session)):
    return JSONResponse(content=list_orders())


@app.get("/admin/users")
def get_user_log(session: Dict[str, Any] = Depends(require_admin_session)):
    return JSONResponse(content=list_users())


@app.get("/admin/accounts")
def get_admin_accounts(session: Dict[str, Any] = Depends(require_admin_session)):
    return JSONResponse(content=list_users())


@app.get("/admin/analytics")
def get_admin_analytics(session: Dict[str, Any] = Depends(require_admin_session)):
    return JSONResponse(content=get_analytics())


@app.get("/admin/market")
def get_admin_market(session: Dict[str, Any] = Depends(require_admin_session)):
    return JSONResponse(content=get_market_snapshot())


@app.get("/admin/tax-table")
def get_admin_tax_table(session: Dict[str, Any] = Depends(require_admin_session)):
    return JSONResponse(content=load_tax_table())


@app.put("/admin/tax-table")
def update_admin_tax_table(
    updates: Dict[str, Any] = Body(...),
    session: Dict[str, Any] = Depends(require_admin_session),
):
    return JSONResponse(content=save_tax_table(updates))


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


@app.get("/tax-table")
def get_public_tax_table():
    return JSONResponse(content=load_tax_table())


@app.post("/quote")
def get_quote(quote_request: QuoteRequest):
    try:
        return JSONResponse(content=build_quote_response(quote_request))
    except ValueError as error:
        return JSONResponse(content={"error": str(error)}, status_code=400)


@app.get("/serial/next")
def get_public_next_serial():
    return {"next_serial": get_next_truemark_serial()}


@app.get("/admin/serial")
def get_next_serial(session: Dict[str, Any] = Depends(require_admin_session)):
    return {"next_serial": get_next_truemark_serial()}
