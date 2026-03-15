from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
INVOICE_DIR = DATA_DIR / "invoices"
VAULT_DIR = DATA_DIR / "vault_packages"
RECEIPT_DIR = DATA_DIR / "receipts"

BRAND_GOLD = colors.HexColor("#C9A227")
BRAND_NAVY = colors.HexColor("#0B1220")
BRAND_MUTED = colors.HexColor("#4B5563")


def ensure_invoice_directories() -> None:
    INVOICE_DIR.mkdir(parents=True, exist_ok=True)
    VAULT_DIR.mkdir(parents=True, exist_ok=True)
    RECEIPT_DIR.mkdir(parents=True, exist_ok=True)


def invoice_path_for(invoice_number: str) -> Path:
    ensure_invoice_directories()
    return INVOICE_DIR / f"{invoice_number}.pdf"


def vault_path_for(serial: str) -> Path:
    ensure_invoice_directories()
    return VAULT_DIR / f"{serial}.zip"


def receipt_path_for(receipt_number: str) -> Path:
    ensure_invoice_directories()
    return RECEIPT_DIR / f"{receipt_number}.pdf"


def _logo_path() -> Path | None:
    candidate_paths = [
        BASE_DIR.parent / "frontend" / "assets" / "TMlogotrans512 - Copy.png",
        BASE_DIR.parent / "frontend" / "assets" / "truemarkseal.png",
    ]

    for path in candidate_paths:
        if path.exists():
            return path

    return None


def _money(value: float | int | None) -> str:
    return f"${float(value or 0.0):,.2f}"


def _line_items(order: Dict[str, Any]) -> list[list[str]]:
    quote_snapshot = order.get("quote_snapshot") or {}
    breakdown = quote_snapshot.get("breakdown") or {}

    return [
        ["Base Mint", _money((breakdown.get("base_nft") or {}).get("total"))],
        ["Package", _money((breakdown.get("package_tier") or {}).get("total"))],
        ["Encryption", _money((breakdown.get("encryption") or {}).get("total"))],
        ["Chain", _money((breakdown.get("chain") or {}).get("total"))],
        ["Storage", _money((breakdown.get("storage") or {}).get("total"))],
        ["Discount", _money(-(float(order.get("discount_amount_usd") or 0.0)))],
        ["Processing Fee", _money(order.get("processing_fee_usd"))],
        ["Tax", _money(order.get("tax_amount_usd"))],
        ["Grand Total", _money(order.get("total_usd"))],
    ]


def generate_invoice_pdf(order: Dict[str, Any]) -> Path:
    ensure_invoice_directories()
    output_path = invoice_path_for(order["invoice_number"])
    document = SimpleDocTemplate(
        str(output_path),
        pagesize=LETTER,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
        title=f"True Mark Invoice {order['invoice_number']}",
    )
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="InvoiceTitle", parent=styles["Heading1"], textColor=BRAND_NAVY, fontSize=22, leading=28))
    styles.add(ParagraphStyle(name="InvoiceMeta", parent=styles["BodyText"], textColor=BRAND_MUTED, fontSize=10, leading=14))
    styles.add(ParagraphStyle(name="SectionTitle", parent=styles["Heading2"], textColor=BRAND_GOLD, fontSize=13, leading=18))

    story = []
    logo_path = _logo_path()
    if logo_path:
        story.append(Image(str(logo_path), width=1.4 * inch, height=1.4 * inch))
        story.append(Spacer(1, 0.15 * inch))

    story.append(Paragraph("True Mark Mint Engine", styles["InvoiceTitle"]))
    story.append(Paragraph("Sales Invoice", styles["SectionTitle"]))
    story.append(Spacer(1, 0.12 * inch))

    header_rows = [
        ["Invoice Number", order["invoice_number"]],
        ["Mint Serial", order["serial"]],
        ["Payment Reference", order.get("payment_reference") or "Not recorded"],
        ["Receipt Number", order.get("receipt_number") or "Not recorded"],
        ["Issued", order["created_at"]],
        ["Status", order.get("status", "completed").title()],
        ["Payment Method", str(order.get("payment_method", "fiat")).title()],
    ]
    if order.get("crypto_token"):
        header_rows.append(
            ["Crypto Reference", f"{order['crypto_token']} @ {_money(order.get('crypto_spot_price_usd'))} spot"]
        )

    header_table = Table(header_rows, colWidths=[1.8 * inch, 4.5 * inch], hAlign="LEFT")
    header_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F4F1E6")),
                ("TEXTCOLOR", (0, 0), (0, -1), BRAND_NAVY),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOX", (0, 0), (-1, -1), 0.4, colors.HexColor("#D1D5DB")),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#E5E7EB")),
            ]
        )
    )
    story.append(header_table)
    story.append(Spacer(1, 0.22 * inch))

    billing_address = ", ".join(
        part
        for part in [
            order.get("billing_address_line1"),
            order.get("billing_address_line2"),
            order.get("billing_city"),
            order.get("billing_state"),
            order.get("billing_postal_code"),
        ]
        if part
    ) or "No billing address on file"

    story.append(Paragraph("Bill To", styles["SectionTitle"]))
    story.append(Paragraph(order.get("user_name") or "Customer", styles["BodyText"]))
    story.append(Paragraph(order.get("user_email") or "", styles["BodyText"]))
    story.append(Paragraph(billing_address, styles["BodyText"]))
    story.append(Paragraph(f"Phone: {order.get('billing_phone') or 'Not provided'}", styles["InvoiceMeta"]))
    story.append(Spacer(1, 0.22 * inch))

    line_item_rows = [["Line Item", "Amount"], *_line_items(order)]
    line_item_table = Table(line_item_rows, colWidths=[4.8 * inch, 1.4 * inch], hAlign="LEFT")
    line_item_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), BRAND_NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                ("TEXTCOLOR", (0, 1), (-1, -1), BRAND_NAVY),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#CBD5E1")),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(Paragraph("Payment Breakdown", styles["SectionTitle"]))
    story.append(line_item_table)
    story.append(Spacer(1, 0.22 * inch))

    tax_rows = [
        ["Applied State", order.get("tax_state") or "Default"],
        ["Applied Tax Rate", f"{float(order.get('tax_rate') or 0.0) * 100:.3f}%"],
    ]
    tax_table = Table(tax_rows, colWidths=[1.8 * inch, 4.5 * inch], hAlign="LEFT")
    tax_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F4F1E6")),
                ("TEXTCOLOR", (0, 0), (0, -1), BRAND_NAVY),
                ("BOX", (0, 0), (-1, -1), 0.4, colors.HexColor("#D1D5DB")),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#E5E7EB")),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    story.append(Paragraph("Tax Table Snapshot", styles["SectionTitle"]))
    story.append(tax_table)
    story.append(Spacer(1, 0.22 * inch))

    story.append(Paragraph("Order Summary", styles["SectionTitle"]))
    story.append(
        Paragraph(
            (
                f"NFT Type: {order.get('nft_type')}<br/>"
                f"Package: {order.get('package_tier')}<br/>"
                f"Encryption: {order.get('encryption')}<br/>"
                f"Chain: {order.get('chain')}<br/>"
                f"Quantity: {order.get('quantity')}<br/>"
                f"File: {order.get('file_name') or 'Not listed'}"
            ),
            styles["BodyText"],
        )
    )
    story.append(Spacer(1, 0.2 * inch))
    story.append(
        Paragraph(
            "This invoice reflects the recorded payment breakdown and tax treatment at the time of order creation inside the True Mark sovereign mint system.",
            styles["InvoiceMeta"],
        )
    )

    document.build(story)
    return output_path


def generate_receipt_pdf(payment_session: Dict[str, Any]) -> Path:
    ensure_invoice_directories()
    output_path = receipt_path_for(payment_session["receipt_number"])
    document = SimpleDocTemplate(
        str(output_path),
        pagesize=LETTER,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
        title=f"True Mark Receipt {payment_session['receipt_number']}",
    )
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="ReceiptTitle", parent=styles["Heading1"], textColor=BRAND_NAVY, fontSize=22, leading=28))
    styles.add(ParagraphStyle(name="ReceiptMeta", parent=styles["BodyText"], textColor=BRAND_MUTED, fontSize=10, leading=14))
    styles.add(ParagraphStyle(name="ReceiptSection", parent=styles["Heading2"], textColor=BRAND_GOLD, fontSize=13, leading=18))

    story = []
    logo_path = _logo_path()
    if logo_path:
        story.append(Image(str(logo_path), width=1.4 * inch, height=1.4 * inch))
        story.append(Spacer(1, 0.15 * inch))

    story.append(Paragraph("True Mark Mint Engine", styles["ReceiptTitle"]))
    story.append(Paragraph("Payment Receipt", styles["ReceiptSection"]))
    story.append(Spacer(1, 0.12 * inch))

    header_rows = [
        ["Receipt Number", payment_session["receipt_number"]],
        ["Payment Reference", payment_session["payment_reference"]],
        ["Captured", payment_session.get("payment_captured_at") or payment_session.get("created_at") or "Pending"],
        ["Status", str(payment_session.get("status", "payment_cleared")).replace("_", " ").title()],
        ["Payment Method", str(payment_session.get("payment_method", "fiat")).title()],
    ]
    if payment_session.get("crypto_token"):
        header_rows.append(
            ["Crypto Reference", f"{payment_session['crypto_token']} @ {_money(payment_session.get('crypto_spot_price_usd'))} spot"]
        )

    header_table = Table(header_rows, colWidths=[1.8 * inch, 4.5 * inch], hAlign="LEFT")
    header_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F4F1E6")),
                ("TEXTCOLOR", (0, 0), (0, -1), BRAND_NAVY),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOX", (0, 0), (-1, -1), 0.4, colors.HexColor("#D1D5DB")),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#E5E7EB")),
            ]
        )
    )
    story.append(header_table)
    story.append(Spacer(1, 0.22 * inch))

    billing_address = ", ".join(
        part
        for part in [
            payment_session.get("billing_address_line1"),
            payment_session.get("billing_address_line2"),
            payment_session.get("billing_city"),
            payment_session.get("billing_state"),
            payment_session.get("billing_postal_code"),
        ]
        if part
    ) or "No billing address on file"

    story.append(Paragraph("Paid By", styles["ReceiptSection"]))
    story.append(Paragraph(payment_session.get("user_name") or "Customer", styles["BodyText"]))
    story.append(Paragraph(payment_session.get("user_email") or "", styles["BodyText"]))
    story.append(Paragraph(billing_address, styles["BodyText"]))
    story.append(Paragraph(f"Phone: {payment_session.get('billing_phone') or 'Not provided'}", styles["ReceiptMeta"]))
    story.append(Spacer(1, 0.22 * inch))

    line_item_rows = [
        ["Line Item", "Amount"],
        ["Estimated Mint Subtotal", _money(payment_session.get("subtotal_usd"))],
        ["Processing Fee", _money(payment_session.get("processing_fee_usd"))],
        ["Estimated Tax", _money(payment_session.get("tax_amount_usd"))],
        ["Payment Total", _money(payment_session.get("total_usd"))],
    ]
    line_item_table = Table(line_item_rows, colWidths=[4.8 * inch, 1.4 * inch], hAlign="LEFT")
    line_item_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), BRAND_NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                ("TEXTCOLOR", (0, 1), (-1, -1), BRAND_NAVY),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#CBD5E1")),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(Paragraph("Payment Summary", styles["ReceiptSection"]))
    story.append(line_item_table)
    story.append(Spacer(1, 0.22 * inch))

    story.append(Paragraph("Workflow Notice", styles["ReceiptSection"]))
    story.append(
        Paragraph(
            (
                "Payment has been captured for this True Mark order. NFT minting is a separate final step. "
                "If the customer cancels after payment and processing has started, a $5.00 cancellation fee applies."
            ),
            styles["BodyText"],
        )
    )
    story.append(Spacer(1, 0.2 * inch))
    story.append(
        Paragraph(
            "This receipt confirms payment clearance only. The final invoice is issued after the NFT mint is completed.",
            styles["ReceiptMeta"],
        )
    )

    document.build(story)
    return output_path
