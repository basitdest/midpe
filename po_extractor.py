"""
extraction/po_extractor.py
Purchase Order field extractor.
"""
import re
from extraction.base_extractor import find_near_keyword, extract_date, extract_amount, extract_table_rows, clean_field


def extract(text: str) -> dict:
    result = {
        "po_number": None,
        "po_date": None,
        "vendor_name": None,
        "ship_to": None,
        "delivery_date": None,
        "items": [],
        "order_total": None,
        "approved_by": None,
        "_raw_text_length": len(text),
    }

    po_match = re.search(r"p\.?o\.?\s*(?:number|no\.?|#)\s*[:\-]?\s*([A-Z0-9\-/]+)", text, re.IGNORECASE)
    if po_match:
        result["po_number"] = clean_field(po_match.group(1))

    result["po_date"]       = extract_date(text, ["po date", "order date", "purchase date", "date"])
    result["delivery_date"] = extract_date(text, ["delivery date", "ship date", "required by", "expected delivery"])
    result["vendor_name"]   = find_near_keyword(text, ["vendor", "supplier", "seller"])
    result["ship_to"]       = find_near_keyword(text, ["ship to", "deliver to", "delivery address"])
    result["order_total"]   = extract_amount(text, ["order total", "total amount", "grand total", "total"])
    result["approved_by"]   = find_near_keyword(text, ["approved by", "authorised by", "authorized by"])
    result["items"]         = extract_table_rows(text, mode="invoice")

    return result