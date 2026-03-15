from __future__ import annotations

import json
import os
import shutil
import uuid
import zipfile
from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import Body, Depends, File, Form, HTTPException, Request, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

try:
    from .auth import authenticate_admin, require_admin_session
    from .invoices import generate_invoice_pdf, invoice_path_for, vault_path_for
    from .mailer import send_invoice_email
    from .main import app
    from .market import get_market_snapshot
    from .pricing import calculate_quote, load_pricing, save_pricing
    from .storage import (
        authenticate_user,
        create_user,
        get_analytics,
        get_next_invoice_number,
        get_next_truemark_serial,
        get_order_by_invoice_number,
        get_order_by_invoice_token,
        get_order_by_vault_token,
        get_user_by_email,
        list_orders,
        list_users,
        record_order,
        update_invoice_delivery,
    )
    from .tax import load_tax_table, resolve_tax_rate, save_tax_table
except ImportError:
    from auth import authenticate_admin, require_admin_session
    from invoices import generate_invoice_pdf, invoice_path_for, vault_path_for
    from mailer import send_invoice_email
    from main import app
    from market import get_market_snapshot
    from pricing import calculate_quote, load_pricing, save_pricing
    from storage import (
        authenticate_user,
        create_user,
        get_analytics,
        get_next_invoice_number,
        get_next_truemark_serial,
        get_order_by_invoice_number,
        get_order_by_invoice_token,
        get_order_by_vault_token,
        get_user_by_email,
        list_orders,
        list_users,
        record_order,
        update_invoice_delivery,
    )
    from tax import load_tax_table, resolve_tax_rate, save_tax_table


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)


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


def _public_url(request: Request, relative_path: str) -> str:
    base_url = str(request.base_url).rstrip("/")
    return f"{base_url}{relative_path}"


def _safe_filename(filename: str | None) -> str:
    candidate = os.path.basename((filename or "").strip())
    return candidate or "uploaded-asset.bin"


def _metadata_payload(metadata: str) -> Any:
    cleaned = metadata.strip()
    if not cleaned:
        return {}

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {"raw": cleaned}


def _write_vault_package(
    output_path: str,
    uploaded_file_path: str,
    original_filename: str,
    metadata: str,
    nft_record: Dict[str, Any],
) -> None:
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.write(uploaded_file_path, arcname=original_filename)
        archive.writestr("metadata.json", json.dumps(_metadata_payload(metadata), indent=2))
        archive.writestr("truemark_record.json", json.dumps(nft_record, indent=2))


def _invoice_file_response(order: Dict[str, Any]) -> FileResponse:
    invoice_path = invoice_path_for(order["invoice_number"])
    if not invoice_path.exists():
        generate_invoice_pdf(order)

    return FileResponse(
        str(invoice_path),
        media_type="application/pdf",
        filename=f"{order['invoice_number']}.pdf",
    )


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
    request: Request,
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
    temp_dir = os.path.join(TEMP_DIR, str(uuid.uuid4()))
    os.makedirs(temp_dir, exist_ok=True)

    original_filename = _safe_filename(file.filename)
    uploaded_file_path = os.path.join(temp_dir, original_filename)
    invoice_path = None
    vault_path = None

    try:
        with open(uploaded_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_size_gb = os.path.getsize(uploaded_file_path) / (1024 * 1024 * 1024)
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

        serial = get_next_truemark_serial()
        invoice_number = get_next_invoice_number()
        invoice_public_token = uuid.uuid4().hex
        vault_public_token = uuid.uuid4().hex
        created_at = datetime.now(timezone.utc).isoformat()

        user = get_user_by_email(email)
        customer_name = name.strip() or (user.get("name") if user else "") or "Customer"
        market_snapshot = get_market_snapshot() if payment_method == "crypto" else None
        crypto_token = None
        crypto_spot_price = None

        if market_snapshot and chain in market_snapshot["assets"]:
            crypto_token = "MATIC" if chain == "polygon" else "ETH"
            crypto_spot_price = market_snapshot["assets"][chain]["usd"]

        invoice_download_url = _public_url(request, f"/downloads/invoices/{invoice_public_token}")
        vault_download_url = _public_url(request, f"/downloads/vault/{vault_public_token}")

        order_payload = {
            "serial": serial,
            "invoice_number": invoice_number,
            "invoice_public_token": invoice_public_token,
            "vault_public_token": vault_public_token,
            "user_id": user.get("id") if user else None,
            "user_email": email,
            "user_name": customer_name,
            "billing_address_line1": user.get("address_line1", "") if user else "",
            "billing_address_line2": user.get("address_line2", "") if user else "",
            "billing_city": user.get("city", "") if user else "",
            "billing_state": user.get("state", "") if user else "",
            "billing_postal_code": user.get("postal_code", "") if user else "",
            "billing_phone": user.get("phone", "") if user else "",
            "billing_dob": user.get("dob", "") if user else "",
            "nft_type": nft_type,
            "package_tier": package_tier,
            "encryption": encryption,
            "chain": chain,
            "quantity": quantity,
            "file_name": original_filename,
            "estimated_storage_gb": file_size_gb,
            "subtotal_usd": quote["total"],
            "tax_rate": quote["tax_rate"],
            "tax_state": quote.get("tax_state") or (user.get("state", "") if user else ""),
            "tax_amount_usd": quote["estimated_tax"],
            "processing_fee_usd": quote["processing_fee"],
            "discount_amount_usd": quote["discount_amount"],
            "total_usd": quote["grand_total"],
            "payment_method": payment_method,
            "crypto_token": crypto_token,
            "crypto_spot_price_usd": crypto_spot_price,
            "quote_snapshot": quote,
            "invoice_email_status": "pending",
            "status": "completed",
            "created_at": created_at,
        }

        nft_record = {
            "serial": serial,
            "invoice_number": invoice_number,
            "invoice_download_url": invoice_download_url,
            "vault_download_url": vault_download_url,
            "customer_name": customer_name,
            "customer_email": email.strip().lower(),
            "nft_type": nft_type,
            "package_tier": package_tier,
            "encryption": encryption,
            "chain": chain,
            "quantity": int(quantity),
            "filename": original_filename,
            "metadata": _metadata_payload(metadata),
            "subtotal_usd": quote["total"],
            "estimated_tax_usd": quote["estimated_tax"],
            "grand_total_usd": quote["grand_total"],
            "payment_method": payment_method,
            "created_at": created_at,
        }

        vault_path = vault_path_for(serial)
        _write_vault_package(
            str(vault_path),
            uploaded_file_path,
            original_filename,
            metadata,
            nft_record,
        )

        invoice_path = generate_invoice_pdf(order_payload)
        record_order(order_payload)

        email_result = {
            "status": "pending",
            "detail": "Invoice email delivery was not attempted.",
            "emailed_at": None,
        }

        try:
            email_result = send_invoice_email(order_payload, invoice_path, invoice_download_url)
        except Exception as error:
            email_result = {
                "status": "failed",
                "detail": f"Invoice email failed: {error}",
                "emailed_at": None,
            }

        update_invoice_delivery(
            invoice_number,
            email_status=email_result["status"],
            sent_to=email.strip().lower(),
            emailed_at=email_result.get("emailed_at"),
        )

        return {
            "serial": serial,
            "invoice_number": invoice_number,
            "invoice_download_url": invoice_download_url,
            "vault_download_url": vault_download_url,
            "invoice_email_status": email_result["status"],
            "invoice_email_detail": email_result["detail"],
            "estimated_tax": quote["estimated_tax"],
            "grand_total": quote["grand_total"],
            "tax_rate": quote["tax_rate"],
            "tax_state": quote.get("tax_state") or "",
        }
    except Exception:
        if invoice_path and os.path.exists(invoice_path):
            os.remove(invoice_path)
        if vault_path and os.path.exists(vault_path):
            os.remove(vault_path)
        raise
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


@app.get("/downloads/invoices/{invoice_token}")
def download_invoice(invoice_token: str):
    order = get_order_by_invoice_token(invoice_token)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found.",
        )

    return _invoice_file_response(order)


@app.get("/downloads/vault/{vault_token}")
def download_vault(vault_token: str):
    order = get_order_by_vault_token(vault_token)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vault package not found.",
        )

    vault_path = vault_path_for(order["serial"])
    if not vault_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vault package is no longer available on the server.",
        )

    return FileResponse(
        str(vault_path),
        media_type="application/zip",
        filename=f"truemark_{order['serial']}_vault.zip",
    )


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


@app.get("/admin/invoices/{invoice_number}/download")
def download_admin_invoice(
    invoice_number: str,
    session: Dict[str, Any] = Depends(require_admin_session),
):
    order = get_order_by_invoice_number(invoice_number)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found.",
        )

    return _invoice_file_response(order)


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
