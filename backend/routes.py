from __future__ import annotations

import json
import os
import shutil
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from fastapi import Body, Depends, File, Form, HTTPException, Request, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

try:
    from .auth import authenticate_admin, require_admin_session
    from .invoices import (
        generate_invoice_pdf,
        generate_receipt_pdf,
        invoice_path_for,
        receipt_path_for,
        vault_path_for,
    )
    from .mailer import send_invoice_email
    from .main import app
    from .market import get_market_snapshot
    from .pricing import calculate_quote, load_pricing, save_pricing
    from .storage import (
        authenticate_user,
        create_payment_session,
        create_user,
        get_analytics,
        get_mint_standard,
        get_next_invoice_number,
        get_next_nft_identifier,
        get_next_payment_reference,
        get_next_receipt_number,
        get_next_truemark_serial,
        get_order_by_invoice_number,
        get_order_by_invoice_token,
        get_order_by_vault_token,
        get_payment_session_by_receipt_token,
        get_payment_session_by_token,
        get_user_by_email,
        list_mint_events,
        list_orders,
        list_users,
        record_order_and_mint_event,
        update_invoice_delivery,
        update_payment_session_status,
    )
    from .tax import load_tax_table, resolve_tax_rate, save_tax_table
except ImportError:
    from auth import authenticate_admin, require_admin_session
    from invoices import (
        generate_invoice_pdf,
        generate_receipt_pdf,
        invoice_path_for,
        receipt_path_for,
        vault_path_for,
    )
    from mailer import send_invoice_email
    from main import app
    from market import get_market_snapshot
    from pricing import calculate_quote, load_pricing, save_pricing
    from storage import (
        authenticate_user,
        create_payment_session,
        create_user,
        get_analytics,
        get_mint_standard,
        get_next_invoice_number,
        get_next_nft_identifier,
        get_next_payment_reference,
        get_next_receipt_number,
        get_next_truemark_serial,
        get_order_by_invoice_number,
        get_order_by_invoice_token,
        get_order_by_vault_token,
        get_payment_session_by_receipt_token,
        get_payment_session_by_token,
        get_user_by_email,
        list_mint_events,
        list_orders,
        list_users,
        record_order_and_mint_event,
        update_invoice_delivery,
        update_payment_session_status,
    )
    from tax import load_tax_table, resolve_tax_rate, save_tax_table


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


BASE_DIR = Path(__file__).resolve().parent
STAGED_UPLOADS_DIR = BASE_DIR / "data" / "payment_sessions"
DALS_EXPORTS_DIR = BASE_DIR / "data" / "dals_exports"
STAGED_UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
DALS_EXPORTS_DIR.mkdir(parents=True, exist_ok=True)


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


class MintFinalizeRequest(BaseModel):
    payment_token: str


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


def _payment_session_directory(payment_reference: str) -> Path:
    directory = STAGED_UPLOADS_DIR / payment_reference
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def _write_vault_package(
    output_path: str,
    staged_file_path: str,
    original_filename: str,
    metadata_payload: Any,
    nft_record: Dict[str, Any],
) -> None:
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.write(staged_file_path, arcname=original_filename)
        archive.writestr("metadata.json", json.dumps(metadata_payload, indent=2))
        archive.writestr("truemark_record.json", json.dumps(nft_record, indent=2))


def _write_dals_export(nft_record: Dict[str, Any]) -> Path:
    output_path = DALS_EXPORTS_DIR / f"{nft_record['nft_identifier']}.json"
    output_path.write_text(json.dumps(nft_record, indent=2), encoding="utf-8")
    return output_path


def _build_public_registry_record(nft_record: Dict[str, Any], mint_standard: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "identifier": nft_record["nft_identifier"],
        "nft_identifier": nft_record["nft_identifier"],
        "identifier_format": mint_standard["identifier_format"],
        "type_code": nft_record.get("type_code"),
        "node_code": nft_record.get("node_id") or mint_standard["node_code"],
        "node_id": nft_record.get("node_id") or mint_standard["node_code"],
        "node_name": mint_standard["node_name"],
        "region": nft_record.get("region_code") or mint_standard["region"],
        "region_code": nft_record.get("region_code") or mint_standard["region"],
        "year": nft_record.get("identifier_year"),
        "identifier_year": nft_record.get("identifier_year"),
        "registrant_code": nft_record.get("registrant_code"),
        "user_identifier": nft_record.get("registrant_code"),
        "sequence": nft_record.get("identifier_sequence"),
        "identifier_sequence": nft_record.get("identifier_sequence"),
        "mint_timestamp": nft_record.get("minted_at"),
        "minted_at": nft_record.get("minted_at"),
        "tm_serial": nft_record.get("serial"),
        "certificate_hash": nft_record.get("certificate_hash"),
        "chain": nft_record.get("chain"),
    }


def _invoice_file_response(order: Dict[str, Any]) -> FileResponse:
    invoice_path = invoice_path_for(order["invoice_number"])
    if not invoice_path.exists():
        generate_invoice_pdf(order)

    return FileResponse(
        str(invoice_path),
        media_type="application/pdf",
        filename=f"{order['invoice_number']}.pdf",
    )


def _receipt_file_response(payment_session: Dict[str, Any]) -> FileResponse:
    receipt_path = receipt_path_for(payment_session["receipt_number"])
    if not receipt_path.exists():
        generate_receipt_pdf(payment_session)

    return FileResponse(
        str(receipt_path),
        media_type="application/pdf",
        filename=f"{payment_session['receipt_number']}.pdf",
    )


def _payment_session_response(payment_session: Dict[str, Any], request: Request) -> Dict[str, Any]:
    return {
        "payment_token": payment_session["payment_public_token"],
        "payment_reference": payment_session["payment_reference"],
        "receipt_number": payment_session["receipt_number"],
        "receipt_download_url": _public_url(request, f"/downloads/receipts/{payment_session['receipt_public_token']}"),
        "status": payment_session["status"],
        "user_name": payment_session["user_name"],
        "user_email": payment_session["user_email"],
        "type_code": payment_session.get("type_code") or "",
        "node_code": payment_session.get("node_id") or get_mint_standard()["node_code"],
        "node_id": payment_session.get("node_id") or get_mint_standard()["node_id"],
        "region": payment_session.get("region_code") or get_mint_standard()["region"],
        "region_code": payment_session.get("region_code") or get_mint_standard()["region_code"],
        "registrant_code": payment_session.get("registrant_code") or "",
        "prefix": payment_session.get("registrant_code") or payment_session.get("prefix") or "",
        "industry": payment_session.get("region_code") or payment_session.get("industry") or "",
        "nft_type": payment_session["nft_type"],
        "package_tier": payment_session["package_tier"],
        "encryption": payment_session["encryption"],
        "chain": payment_session["chain"],
        "quantity": payment_session["quantity"],
        "file_name": payment_session.get("file_name"),
        "payment_method": payment_session["payment_method"],
        "subtotal_usd": payment_session["subtotal_usd"],
        "tax_amount_usd": payment_session["tax_amount_usd"],
        "total_usd": payment_session["total_usd"],
        "tax_rate": payment_session["tax_rate"],
        "tax_state": payment_session.get("tax_state") or "",
        "processing_fee_usd": payment_session["processing_fee_usd"],
        "discount_amount_usd": payment_session["discount_amount_usd"],
        "cancellation_fee_usd": payment_session["cancellation_fee_usd"],
        "refund_due_usd": payment_session.get("refund_due_usd"),
        "payment_captured_at": payment_session.get("payment_captured_at"),
        "canceled_at": payment_session.get("canceled_at"),
        "minted_at": payment_session.get("minted_at"),
        "minted_serial": payment_session.get("minted_serial"),
        "minted_nft_identifier": payment_session.get("minted_nft_identifier"),
        "minted_invoice_number": payment_session.get("minted_invoice_number"),
        "quote_snapshot": payment_session.get("quote_snapshot"),
    }


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


@app.post("/payments/process")
def process_payment(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    registrant_code: str = Form(""),
    region_code: str = Form(""),
    prefix: str = Form(""),
    industry: str = Form(""),
    nft_type: str = Form(...),
    file: UploadFile = File(...),
    metadata: str = Form(...),
    package_tier: str = Form("starter"),
    encryption: str = Form("none"),
    chain: str = Form("polygon"),
    quantity: int = Form(1),
    payment_method: str = Form("fiat"),
):
    mint_standard = get_mint_standard()
    resolved_registrant_code = (registrant_code or prefix).strip().upper() or "PUBLIC"
    resolved_region_code = (region_code or industry).strip().upper() or mint_standard["region_code"]
    payment_reference = get_next_payment_reference()
    receipt_number = get_next_receipt_number()
    payment_public_token = uuid.uuid4().hex
    receipt_public_token = uuid.uuid4().hex
    captured_at = datetime.now(timezone.utc).isoformat()

    stage_dir = _payment_session_directory(payment_reference)
    original_filename = _safe_filename(file.filename)
    staged_file_path = stage_dir / original_filename
    receipt_path = None

    try:
        with open(staged_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_size_gb = staged_file_path.stat().st_size / (1024 * 1024 * 1024)
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

        user = get_user_by_email(email)
        customer_name = name.strip() or (user.get("name") if user else "") or "Customer"
        metadata_payload = _metadata_payload(metadata)
        market_snapshot = get_market_snapshot() if payment_method == "crypto" else None
        crypto_token = None
        crypto_spot_price = None

        if market_snapshot and chain in market_snapshot["assets"]:
            crypto_token = "MATIC" if chain == "polygon" else "ETH"
            crypto_spot_price = market_snapshot["assets"][chain]["usd"]

        payment_session = {
            "payment_reference": payment_reference,
            "payment_public_token": payment_public_token,
            "receipt_number": receipt_number,
            "receipt_public_token": receipt_public_token,
            "type_code": mint_standard["type_codes"].get(nft_type, nft_type),
            "node_id": mint_standard["node_id"],
            "region_code": resolved_region_code,
            "registrant_code": resolved_registrant_code,
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
            "prefix": resolved_registrant_code,
            "industry": resolved_region_code,
            "nft_type": nft_type,
            "package_tier": package_tier,
            "encryption": encryption,
            "chain": chain,
            "quantity": quantity,
            "file_name": original_filename,
            "staged_file_path": str(staged_file_path),
            "estimated_storage_gb": file_size_gb,
            "metadata": metadata_payload,
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
            "cancellation_fee_usd": 5.0,
            "payment_captured_at": captured_at,
            "status": "payment_cleared",
            "created_at": captured_at,
            "updated_at": captured_at,
        }

        receipt_path = generate_receipt_pdf(payment_session)
        create_payment_session(payment_session)

        response_payload = _payment_session_response(payment_session, request)
        response_payload["message"] = (
            "Payment cleared. Return to Mint to finalize the NFT. A $5 cancellation fee applies if you cancel after payment."
        )
        return response_payload
    except Exception:
        if receipt_path and receipt_path.exists():
            receipt_path.unlink()
        shutil.rmtree(stage_dir, ignore_errors=True)
        raise


@app.get("/payments/{payment_token}")
def get_payment_session(payment_token: str, request: Request):
    payment_session = get_payment_session_by_token(payment_token)
    if not payment_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment session not found.",
        )

    return _payment_session_response(payment_session, request)


@app.post("/payments/{payment_token}/cancel")
def cancel_payment(payment_token: str, request: Request):
    payment_session = get_payment_session_by_token(payment_token)
    if not payment_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment session not found.",
        )

    if payment_session["status"] == "minted":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This payment has already been minted and can no longer be canceled.",
        )

    if payment_session["status"] == "canceled_after_payment":
        return _payment_session_response(payment_session, request)

    refund_due_usd = max(float(payment_session["total_usd"]) - float(payment_session["cancellation_fee_usd"]), 0.0)
    canceled_at = datetime.now(timezone.utc).isoformat()
    update_payment_session_status(
        payment_token,
        status="canceled_after_payment",
        refund_due_usd=refund_due_usd,
        canceled_at=canceled_at,
    )

    staged_file_path = payment_session.get("staged_file_path")
    if staged_file_path:
        shutil.rmtree(Path(staged_file_path).parent, ignore_errors=True)

    updated_session = get_payment_session_by_token(payment_token)
    response_payload = _payment_session_response(updated_session, request)
    response_payload["message"] = (
        f"Payment canceled. A $5.00 cancellation fee was retained and ${refund_due_usd:.2f} remains eligible for refund handling."
    )
    return response_payload


@app.post("/mint/complete")
def mint_nft(request: Request, payload: MintFinalizeRequest):
    mint_standard = get_mint_standard()
    payment_session = get_payment_session_by_token(payload.payment_token)
    if not payment_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment session not found.",
        )

    if payment_session["status"] == "canceled_after_payment":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This payment was canceled and can no longer be minted.",
        )

    if payment_session["status"] == "minted":
        existing_order = get_order_by_invoice_number(payment_session["minted_invoice_number"])
        if not existing_order:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="The mint was recorded, but the linked order record could not be found.",
            )
        return {
            "serial": payment_session.get("minted_serial"),
            "nft_identifier": payment_session.get("minted_nft_identifier"),
            "invoice_number": payment_session.get("minted_invoice_number"),
            "node_code": payment_session.get("node_id"),
            "node_id": payment_session.get("node_id"),
            "region": payment_session.get("region_code"),
            "region_code": payment_session.get("region_code"),
            "registrant_code": payment_session.get("registrant_code"),
            "invoice_download_url": _public_url(request, f"/downloads/invoices/{existing_order['invoice_public_token']}"),
            "vault_download_url": _public_url(request, f"/downloads/vault/{existing_order['vault_public_token']}"),
            "receipt_download_url": _public_url(request, f"/downloads/receipts/{payment_session['receipt_public_token']}"),
            "message": "This payment session was already minted.",
        }

    staged_file_path = Path(payment_session.get("staged_file_path") or "")
    if not staged_file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="The staged source file is no longer available. Please upload and pay again.",
        )

    serial = get_next_truemark_serial()
    invoice_number = get_next_invoice_number()
    invoice_public_token = uuid.uuid4().hex
    vault_public_token = uuid.uuid4().hex
    minted_at = datetime.now(timezone.utc).isoformat()
    nft_identifier, identifier_year, identifier_sequence, type_code = get_next_nft_identifier(
        payment_session["nft_type"],
        payment_session.get("node_id"),
        payment_session.get("region_code"),
        payment_session.get("registrant_code"),
        minted_at,
    )
    invoice_download_url = _public_url(request, f"/downloads/invoices/{invoice_public_token}")
    vault_download_url = _public_url(request, f"/downloads/vault/{vault_public_token}")
    receipt_download_url = _public_url(request, f"/downloads/receipts/{payment_session['receipt_public_token']}")
    invoice_path = None
    vault_path = None
    registry_export_path = None

    try:
        order_payload = {
            "serial": serial,
            "nft_identifier": nft_identifier,
            "type_code": type_code,
            "node_id": payment_session.get("node_id"),
            "region_code": payment_session.get("region_code"),
            "registrant_code": payment_session.get("registrant_code"),
            "identifier_year": identifier_year,
            "identifier_sequence": identifier_sequence,
            "invoice_number": invoice_number,
            "invoice_public_token": invoice_public_token,
            "vault_public_token": vault_public_token,
            "payment_reference": payment_session["payment_reference"],
            "receipt_number": payment_session["receipt_number"],
            "user_id": payment_session.get("user_id"),
            "user_email": payment_session["user_email"],
            "user_name": payment_session["user_name"],
            "billing_address_line1": payment_session.get("billing_address_line1", ""),
            "billing_address_line2": payment_session.get("billing_address_line2", ""),
            "billing_city": payment_session.get("billing_city", ""),
            "billing_state": payment_session.get("billing_state", ""),
            "billing_postal_code": payment_session.get("billing_postal_code", ""),
            "billing_phone": payment_session.get("billing_phone", ""),
            "billing_dob": payment_session.get("billing_dob", ""),
            "prefix": payment_session.get("registrant_code", ""),
            "industry": payment_session.get("region_code", ""),
            "nft_type": payment_session["nft_type"],
            "package_tier": payment_session["package_tier"],
            "encryption": payment_session["encryption"],
            "chain": payment_session["chain"],
            "quantity": payment_session["quantity"],
            "file_name": payment_session.get("file_name"),
            "estimated_storage_gb": payment_session.get("estimated_storage_gb", 0.0),
            "subtotal_usd": payment_session["subtotal_usd"],
            "tax_rate": payment_session["tax_rate"],
            "tax_state": payment_session.get("tax_state", ""),
            "tax_amount_usd": payment_session["tax_amount_usd"],
            "processing_fee_usd": payment_session["processing_fee_usd"],
            "discount_amount_usd": payment_session["discount_amount_usd"],
            "total_usd": payment_session["total_usd"],
            "payment_method": payment_session["payment_method"],
            "crypto_token": payment_session.get("crypto_token"),
            "crypto_spot_price_usd": payment_session.get("crypto_spot_price_usd"),
            "quote_snapshot": payment_session.get("quote_snapshot", {}),
            "invoice_email_status": "pending",
            "status": "minted",
            "created_at": minted_at,
        }

        metadata_payload = payment_session.get("metadata", {})
        nft_record = {
            "identifier": nft_identifier,
            "identifier_format": mint_standard["identifier_format"],
            "serial": serial,
            "nft_identifier": nft_identifier,
            "type_code": type_code,
            "node_id": payment_session.get("node_id"),
            "region_code": payment_session.get("region_code"),
            "registrant_code": payment_session.get("registrant_code"),
            "identifier_year": identifier_year,
            "identifier_sequence": identifier_sequence,
            "invoice_number": invoice_number,
            "payment_reference": payment_session["payment_reference"],
            "receipt_number": payment_session["receipt_number"],
            "invoice_download_url": invoice_download_url,
            "vault_download_url": vault_download_url,
            "receipt_download_url": receipt_download_url,
            "customer_name": payment_session["user_name"],
            "customer_email": payment_session["user_email"],
            "prefix": payment_session.get("registrant_code", ""),
            "industry": payment_session.get("region_code", ""),
            "nft_type": payment_session["nft_type"],
            "package_tier": payment_session["package_tier"],
            "encryption": payment_session["encryption"],
            "chain": payment_session["chain"],
            "quantity": int(payment_session["quantity"]),
            "filename": payment_session.get("file_name"),
            "metadata": metadata_payload,
            "subtotal_usd": payment_session["subtotal_usd"],
            "estimated_tax_usd": payment_session["tax_amount_usd"],
            "grand_total_usd": payment_session["total_usd"],
            "payment_method": payment_session["payment_method"],
            "minted_at": minted_at,
        }

        vault_path = vault_path_for(serial)
        _write_vault_package(
            str(vault_path),
            str(staged_file_path),
            payment_session.get("file_name") or staged_file_path.name,
            metadata_payload,
            nft_record,
        )
        registry_export_path = _write_dals_export(_build_public_registry_record(nft_record, mint_standard))

        invoice_path = generate_invoice_pdf(order_payload)
        order_row = record_order_and_mint_event(
            order_payload,
            {
                "payment_reference": payment_session["payment_reference"],
                "receipt_number": payment_session["receipt_number"],
                "invoice_number": invoice_number,
                "serial": serial,
                "nft_identifier": nft_identifier,
                "type_code": type_code,
                "node_id": payment_session.get("node_id"),
                "region_code": payment_session.get("region_code"),
                "registrant_code": payment_session.get("registrant_code"),
                "identifier_year": identifier_year,
                "identifier_sequence": identifier_sequence,
                "prefix": payment_session.get("registrant_code", ""),
                "industry": payment_session.get("region_code", ""),
                "nft_type": payment_session["nft_type"],
                "package_tier": payment_session["package_tier"],
                "encryption": payment_session["encryption"],
                "chain": payment_session["chain"],
                "quantity": payment_session["quantity"],
                "user_id": payment_session.get("user_id"),
                "user_email": payment_session["user_email"],
                "user_name": payment_session["user_name"],
                "file_name": payment_session.get("file_name"),
                "metadata": metadata_payload,
                "payment_method": payment_session["payment_method"],
                "subtotal_usd": payment_session["subtotal_usd"],
                "tax_amount_usd": payment_session["tax_amount_usd"],
                "total_usd": payment_session["total_usd"],
                "minted_at": minted_at,
                "created_at": minted_at,
            },
        )

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
            sent_to=payment_session["user_email"],
            emailed_at=email_result.get("emailed_at"),
        )
        update_payment_session_status(
            payload.payment_token,
            status="minted",
            minted_order_id=order_row["id"],
            minted_serial=serial,
            minted_nft_identifier=nft_identifier,
            minted_invoice_number=invoice_number,
            minted_at=minted_at,
        )
        shutil.rmtree(staged_file_path.parent, ignore_errors=True)

        return {
            "serial": serial,
            "nft_identifier": nft_identifier,
            "invoice_number": invoice_number,
            "node_code": payment_session.get("node_id"),
            "node_id": payment_session.get("node_id"),
            "region": payment_session.get("region_code"),
            "region_code": payment_session.get("region_code"),
            "registrant_code": payment_session.get("registrant_code"),
            "payment_reference": payment_session["payment_reference"],
            "receipt_number": payment_session["receipt_number"],
            "invoice_download_url": invoice_download_url,
            "vault_download_url": vault_download_url,
            "receipt_download_url": receipt_download_url,
            "invoice_email_status": email_result["status"],
            "invoice_email_detail": email_result["detail"],
            "dals_export_file": registry_export_path.name if registry_export_path else None,
            "grand_total": payment_session["total_usd"],
            "message": "Mint completed. Your invoice, receipt, and vault package are ready.",
        }
    except Exception:
        if invoice_path and invoice_path.exists():
            invoice_path.unlink()
        if vault_path and vault_path.exists():
            vault_path.unlink()
        if registry_export_path and registry_export_path.exists():
            registry_export_path.unlink()
        raise


@app.get("/downloads/receipts/{receipt_token}")
def download_receipt(receipt_token: str):
    payment_session = get_payment_session_by_receipt_token(receipt_token)
    if not payment_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receipt not found.",
        )

    return _receipt_file_response(payment_session)


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
    return JSONResponse(content=list_mint_events())


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


@app.get("/mint-standard")
def get_public_mint_standard():
    return JSONResponse(content=get_mint_standard())


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
    return {
        "next_serial": get_next_truemark_serial(),
        **get_mint_standard(),
    }


@app.get("/admin/serial")
def get_next_serial(session: Dict[str, Any] = Depends(require_admin_session)):
    return {"next_serial": get_next_truemark_serial()}
