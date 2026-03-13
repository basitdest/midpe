"""
midpe/extraction/invoice_extractor.py
Invoice field extractor — supports English and Spanish/CFDI (Mexican) invoices.
"""

import re
from midpe.extraction.base_extractor import (
    find_near_keyword, extract_date, clean_field, parse_amount_european
)


def _find_amount(text: str, keywords: list) -> str | None:
    """
    Find a monetary amount near any of the given keywords.
    Handles European format ($3.525,00 or $35,00 → 3525.00 or 35.00).
    Also looks on the NEXT line after the keyword (common in CFDI PDFs).
    """
    lines = text.split("\n")
    for i, line in enumerate(lines):
        for kw in keywords:
            if re.search(re.escape(kw), line, re.IGNORECASE):
                # Search same line first
                amt = re.search(r"\$\s*([\d.]+,\d{2}|[\d,]+\.\d{2}|\d+,\d{2})", line)
                if amt:
                    return parse_amount_european(amt.group(1))
                # Then look on the next line
                if i + 1 < len(lines):
                    amt = re.search(r"\$\s*([\d.]+,\d{2}|[\d,]+\.\d{2}|\d+,\d{2})", lines[i + 1])
                    if amt:
                        return parse_amount_european(amt.group(1))
    return None


def extract(text: str) -> dict:
    result = {
        "invoice_number":   None,
        "invoice_date":     None,
        "due_date":         None,
        "vendor_name":      None,
        "bill_to":          None,
        "line_items":       [],
        "subtotal":         None,
        "tax_amount":       None,
        "discount":         None,
        "total_amount":     None,
        "currency":         None,
        "payment_terms":    None,
        "payment_method":   None,
        "_raw_text_length": len(text),
    }

    # ── Invoice Number ────────────────────────────────────────
    for p in [
        r"folio\s*[:\-]?\s*([A-Z0-9\-/]{3,})",
        r"factura\s+(?:de\s+venta\s+)?#\s*([A-Z0-9\-/]{3,})",
        r"invoice\s*(?:number|no\.?|#)\s*[:\-]?\s*([A-Z0-9\-/]{3,})",
    ]:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            val = clean_field(m.group(1))
            if len(val) >= 3:
                result["invoice_number"] = val
                break

    # ── Dates ─────────────────────────────────────────────────
    result["invoice_date"] = extract_date(text, [
        "emisión", "emision", "invoice date", "bill date", "date of invoice"
    ])
    result["due_date"] = extract_date(text, [
        "fecha de vencimiento", "vencimiento", "due date", "payment due"
    ])

    # ── Vendor (Emisor) ───────────────────────────────────────
    # In CFDI: "SAT Nombre registrado: NOWPORTS MEXICO" is the emisor name
    for p in [
        r"rfc\s*:\s*[A-Z0-9]+\s*\nsat\s+nombre\s+registrado\s*:\s*(.+?)(?:\n|$)",
        r"sat\s+nombre\s+registrado\s*:\s*(.+?)(?:\n|$)",
        r"(?:from|vendor|seller|emisor)\s*[:\-]?\s*(.+?)(?:\n|$)",
    ]:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            val = clean_field(m.group(1))
            # Reject if it's blank or just says "SAT Nombre registrado:" again (receptor blank line issue)
            if val and len(val) > 2 and "multibrand" not in val.lower() and "sat nombre" not in val.lower():
                result["vendor_name"] = val
                break

    # ── Bill To (Receptor) ────────────────────────────────────
    # In this CFDI PDF the layout is:
    #   Line N:   "Facturar a"
    #   Line N+1: "O15027,O15030,..."   ← order refs, SKIP
    #   Line N+2: "MULTIBRAND OUTLET STORES"  ← this is what we want
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if re.search(r"facturar\s+a", line, re.IGNORECASE):
            # Look ahead up to 4 lines for a company name
            for j in range(i + 1, min(i + 5, len(lines))):
                candidate = lines[j].strip()
                # Skip order reference lines like "O15027,O15030,..."
                if re.match(r"^[A-Z]\d+,", candidate):
                    continue
                # Skip blank lines
                if not candidate:
                    continue
                # Skip address-like lines (contain #, digits, postal codes)
                if re.search(r"\d{4,}|BLVD|PISO|COL\.|MEX,", candidate, re.IGNORECASE):
                    continue
                result["bill_to"] = candidate
                break
            break

    # Fallback for English invoices
    if not result["bill_to"]:
        m = re.search(r"(?:bill\s+to|customer)\s*[:\-]?\s*(.+?)(?:\n|$)", text, re.IGNORECASE)
        if m:
            result["bill_to"] = clean_field(m.group(1))

    # ── Currency ──────────────────────────────────────────────
    m = re.search(r"(?:moneda|currency)\s*[:\-]?\s*([A-Z]{3})", text, re.IGNORECASE)
    if m:
        result["currency"] = m.group(1)

    # ── Amounts ───────────────────────────────────────────────
    result["subtotal"] = _find_amount(text, ["subtotal:"])
    result["tax_amount"] = _find_amount(text, [
        "total de transferencia de impuestos",
        "total impuestos transferidos",
        "tax amount", "iva:", "vat:"
    ])
    result["discount"] = _find_amount(text, ["descuento:", "discount:"])
    result["total_amount"] = _find_amount(text, [
        "total:", "total\n", "grand total", "total amount due"
    ])

    # ── Payment Terms / Method ────────────────────────────────
    m = re.search(r"(?:términos|terminos|terms?)\s*[:\-]?\s*(.+?)(?:\n|$)", text, re.IGNORECASE)
    if m:
        result["payment_terms"] = clean_field(m.group(1))

    m = re.search(r"(?:sat\s+método\s+de\s+pago|método\s+de\s+pago|payment\s+method)\s*[:\-]?\s*(.+?)(?:\n|$)", text, re.IGNORECASE)
    if m:
        result["payment_method"] = clean_field(m.group(1))

    # ── Line Items ────────────────────────────────────────────
    result["line_items"] = _extract_line_items(text)

    return result


def _extract_line_items(text: str) -> list:
    """
    Extract service line items from CFDI-format invoice tables.

    In raw pdfplumber text, each item spans multiple lines:
      "1,0 A9 - Tarifa 78101702 - Servicios de transporte ... $35,00 $0,00 $35,00"
      "AMS"                          ← service sub-label on next line
      "TRANSFERENCIAS"               ← tax breakdown header, skip
      "35,00 002 Tasa 0,000 0,00"   ← tax details, skip
    """
    items = []

    # Lines to skip entirely
    skip_re = re.compile(
        r"([A-Za-z0-9+/]{30,}={0,2})"           # base64 blocks
        r"|\|\|[\d.]+\|"                          # cadena original delimiter
        r"|^transferencias$"                       # tax section header
        r"|^(base\s+impuesto|cantidad\s+unidades|sat\s+número)" # table headers
        r"|^(este|de\s+un\s+cfdi|es\s+una|representac)",        # boilerplate
        re.IGNORECASE
    )

    # CFDI line item pattern:
    # qty  unit-Tarifa  sat_code - description ... tax_flag  $price  $discount  $amount
    cfdi_re = re.compile(
        r"^(\d+[,.]?\d*)"                          # qty: "1,0"
        r"\s+([A-Z]\d+)\s+-\s+Tarifa\s+"           # unit: "A9 - Tarifa"
        r"(\d{5,8})\s+-\s+(.+?)"                   # SAT code + description
        r"\s+\$\s*([\d.,]+)"                        # unit price
        r"\s+\$\s*([\d.,]+)"                        # discount
        r"\s+\$\s*([\d.,]+)\s*$",                   # amount
        re.IGNORECASE
    )

    # English/simple invoice pattern
    simple_re = re.compile(
        r"^(.{5,60}?)\s{2,}(\d+)\s+\$?([\d,.]+)\s+\$?([\d,.]+)\s*$"
    )

    lines = text.split("\n")
    prev_was_item = False

    for line in lines:
        s = line.strip()
        if not s:
            prev_was_item = False
            continue
        if skip_re.search(s):
            prev_was_item = False
            continue

        m = cfdi_re.match(s)
        if m:
            desc = clean_field(m.group(4))
            # Strip trailing tax-status text that bleeds in: "01 - No" / "02 - Sí"
            desc = re.sub(r"\s+0\d\s*-\s*(No|Sí|Si)\s*$", "", desc, flags=re.IGNORECASE).strip()
            items.append({
                "quantity":    m.group(1).replace(",", "."),
                "unit":        m.group(2),
                "sat_code":    m.group(3),
                "description": desc,
                "unit_price":  parse_amount_european(m.group(5)),
                "discount":    parse_amount_european(m.group(6)),
                "amount":      parse_amount_european(m.group(7)),
            })
            prev_was_item = True
            continue

        # Sub-label line immediately after a CFDI item (e.g. "AMS", "Telex Release")
        if prev_was_item and items:
            if (len(s) < 60
                    and not re.match(r"^[\d.,]+\s+\d{3}", s)
                    and not s.upper().startswith("TRANSFERENCIA")
                    and not s.upper().startswith("BASE")
                    and "objeto de" not in s.lower()):
                # Also clean up any trailing "objeto de" bleed-in
                label = re.sub(r"\s+objeto\s+de.*$", "", s, flags=re.IGNORECASE).strip()
                if label:
                    items[-1]["service_label"] = label
            prev_was_item = False
            continue

        m2 = simple_re.match(s)
        if m2:
            items.append({
                "description": clean_field(m2.group(1)),
                "quantity":    m2.group(2),
                "unit_price":  parse_amount_european(m2.group(3)),
                "amount":      parse_amount_european(m2.group(4)),
            })
            prev_was_item = False

    return items
