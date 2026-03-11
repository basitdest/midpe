"""
extraction/invoice_extractor.py
Invoice-specific field extractor.

Extracts:
  - Invoice number, date, due date
  - Vendor / billed-to name
  - Line items (description, qty, unit price, amount)
  - Subtotal, tax, total
  - Payment terms
"""

import re
from extraction.base_extractor import (
    find_near_keyword, extract_date, extract_amount,
    extract_table_rows, clean_field
)


def extract(text: str) -> dict:
    """
    Main entry point. Returns structured invoice data.
    """
    result = {
        "invoice_number": None,
        "invoice_date": None,
        "due_date": None,
        "vendor_name": None,
        "bill_to": None,
        "line_items": [],
        "subtotal": None,
        "tax_amount": None,
        "total_amount": None,
        "payment_terms": None,
        "_raw_text_length": len(text),
    }

    # ── Invoice Number ────────────────────────
    inv_patterns = [
        r"invoice\s*(?:number|no\.?|#)\s*[:\-]?\s*([A-Z0-9\-/]+)",
        r"inv\s*#?\s*[:\-]?\s*([A-Z0-9\-/]+)",
        r"bill\s*(?:number|no\.?)\s*[:\-]?\s*([A-Z0-9\-/]+)",
    ]
    for p in inv_patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            result["invoice_number"] = clean_field(m.group(1))
            break

    # ── Dates ────────────────────────────────
    result["invoice_date"] = extract_date(text, ["invoice date", "date of invoice", "bill date", "date"])
    result["due_date"]     = extract_date(text, ["due date", "payment due", "pay by"])

    # ── Vendor / Bill To ─────────────────────
    vendor_match = re.search(
        r"(?:from|vendor|seller|billed?\s+by)\s*[:\-]?\s*(.+?)(?:\n|,|$)",
        text, re.IGNORECASE
    )
    if vendor_match:
        result["vendor_name"] = clean_field(vendor_match.group(1))

    bill_match = re.search(
        r"(?:bill\s+to|billed?\s+to|client|customer)\s*[:\-]?\s*(.+?)(?:\n|,|$)",
        text, re.IGNORECASE
    )
    if bill_match:
        result["bill_to"] = clean_field(bill_match.group(1))

    # ── Amounts ──────────────────────────────
    result["subtotal"]    = extract_amount(text, ["subtotal", "sub total", "sub-total", "net amount"])
    result["tax_amount"]  = extract_amount(text, ["tax amount", "gst", "vat", "tax", "hst"])
    result["total_amount"] = extract_amount(text, [
        "total amount due", "total due", "amount due",
        "grand total", "total amount", "total"
    ])

    # ── Payment Terms ─────────────────────────
    terms_match = re.search(
        r"payment\s+terms?\s*[:\-]?\s*(.+?)(?:\n|$)",
        text, re.IGNORECASE
    )
    if terms_match:
        result["payment_terms"] = clean_field(terms_match.group(1))

    # ── Line Items (table rows) ───────────────
    result["line_items"] = extract_table_rows(text, mode="invoice")

    return result