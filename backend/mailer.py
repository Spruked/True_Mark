from __future__ import annotations

import os
import smtplib
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path
from typing import Any, Dict


BASE_DIR = Path(__file__).resolve().parent
OUTBOX_DIR = BASE_DIR / "data" / "mail_outbox"


def _bool_env(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _smtp_config() -> Dict[str, Any]:
    return {
        "host": os.getenv("TRUEMARK_SMTP_HOST", "").strip(),
        "port": int(os.getenv("TRUEMARK_SMTP_PORT", "587").strip()),
        "username": os.getenv("TRUEMARK_SMTP_USERNAME", "").strip(),
        "password": os.getenv("TRUEMARK_SMTP_PASSWORD", ""),
        "from_email": os.getenv("TRUEMARK_INVOICE_FROM_EMAIL", "invoices@truemark.spruked.com").strip(),
        "from_name": os.getenv("TRUEMARK_INVOICE_FROM_NAME", "True Mark Mint Engine").strip(),
        "use_ssl": _bool_env("TRUEMARK_SMTP_USE_SSL", False),
        "use_starttls": _bool_env("TRUEMARK_SMTP_USE_STARTTLS", True),
    }


def _build_message(order: Dict[str, Any], invoice_path: Path, invoice_url: str) -> EmailMessage:
    message = EmailMessage()
    config = _smtp_config()
    from_name = config["from_name"]
    from_email = config["from_email"]
    message["From"] = f"{from_name} <{from_email}>"
    message["To"] = order["user_email"]
    message["Subject"] = f"True Mark Invoice {order['invoice_number']}"

    text_body = (
        f"Hello {order['user_name']},\n\n"
        f"Your True Mark invoice {order['invoice_number']} is attached.\n"
        f"Mint serial: {order['serial']}\n"
        f"Grand total: ${float(order.get('total_usd') or 0.0):.2f}\n\n"
        f"You can also download the invoice here:\n{invoice_url}\n\n"
        "Thank you,\nTrue Mark Mint Engine\n"
    )
    message.set_content(text_body)

    pdf_bytes = invoice_path.read_bytes()
    message.add_attachment(
        pdf_bytes,
        maintype="application",
        subtype="pdf",
        filename=invoice_path.name,
    )
    return message


def send_invoice_email(order: Dict[str, Any], invoice_path: Path, invoice_url: str) -> Dict[str, Any]:
    config = _smtp_config()
    message = _build_message(order, invoice_path, invoice_url)

    if not config["host"]:
        OUTBOX_DIR.mkdir(parents=True, exist_ok=True)
        outbox_path = OUTBOX_DIR / f"{order['invoice_number']}.eml"
        outbox_path.write_bytes(message.as_bytes())
        return {
            "status": "queued_local",
            "detail": "SMTP is not configured yet. The invoice email was queued in the local outbox.",
            "emailed_at": datetime.now(timezone.utc).isoformat(),
        }

    if config["use_ssl"]:
        smtp = smtplib.SMTP_SSL(config["host"], config["port"], timeout=20)
    else:
        smtp = smtplib.SMTP(config["host"], config["port"], timeout=20)

    try:
        smtp.ehlo()
        if config["use_starttls"] and not config["use_ssl"]:
            smtp.starttls()
            smtp.ehlo()

        if config["username"]:
            smtp.login(config["username"], config["password"])

        smtp.send_message(message)
        return {
            "status": "sent",
            "detail": f"Invoice emailed to {order['user_email']}.",
            "emailed_at": datetime.now(timezone.utc).isoformat(),
        }
    finally:
        smtp.quit()
