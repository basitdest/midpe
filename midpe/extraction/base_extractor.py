"""
extraction/base_extractor.py
Shared utility functions used by all document-specific extractors.

Provides:
  - find_near_keyword()  → layout anchoring
  - extract_date()       → smart date extraction with multiple formats
  - extract_amount()     → currency/numeric amount extraction
  - extract_table_rows() → tabular line-item parsing
  - clean_field()        → strip noise from extracted strings
  - extract_all_kv()     → generic key-value pair extraction
  - extract_named_entities() → basic NE extraction (no spaCy required)
"""

import re
from datetime import datetime
from typing import Optional, List, Dict, Any


# ─────────────────────────────────────────────
# TEXT CLEANING
# ─────────────────────────────────────────────

def clean_field(value: str) -> str:
    """Remove common noise characters from extracted text."""
    if not value:
        return ""
    value = value.strip().strip(":,-/|")
    value = re.sub(r"\s{2,}", " ", value)
    return value.strip()


# ─────────────────────────────────────────────
# LAYOUT ANCHORING — find value near a keyword
# ─────────────────────────────────────────────

def find_near_keyword(text: str, keywords: list, window: int = 80) -> Optional[str]:
    """
    For each keyword, search the text and return the first non-empty
    value found within `window` characters after the keyword.
    Strategy C implementation.
    """
    for kw in keywords:
        pattern = re.escape(kw) + r"\s*[:\-]?\s*(.{1," + str(window) + r"}?)(?:\n|$)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            val = clean_field(match.group(1))
            if val:
                return val
    return None


# ─────────────────────────────────────────────
# DATE EXTRACTION
# ─────────────────────────────────────────────

DATE_FORMATS = [
    "%d/%m/%Y", "%m/%d/%Y", "%Y-%m-%d",
    "%d-%m-%Y", "%d %B %Y", "%d %b %Y",
    "%B %d, %Y", "%b %d, %Y",
    "%B %Y", "%b %Y",
    "%d.%m.%Y",
]

DATE_REGEX = r"""
    (?:
        \d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}     # dd/mm/yyyy or mm-dd-yyyy
        |
        \d{4}[\/\-\.]\d{1,2}[\/\-\.]\d{1,2}         # yyyy-mm-dd
        |
        \d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}
        |
        (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}
        |
        (?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}
    )
"""

def extract_date(text: str, anchor_keywords: list) -> Optional[str]:
    """
    Find a date near any of the anchor keywords.
    Returns ISO format date string or raw string if parsing fails.
    """
    for kw in anchor_keywords:
        # Find keyword position
        kw_match = re.search(re.escape(kw), text, re.IGNORECASE)
        if not kw_match:
            continue
        start = kw_match.end()
        snippet = text[start: start + 120]

        date_match = re.search(DATE_REGEX, snippet, re.IGNORECASE | re.VERBOSE)
        if date_match:
            raw_date = date_match.group(0).strip()
            # Try to parse and normalize
            for fmt in DATE_FORMATS:
                try:
                    dt = datetime.strptime(raw_date, fmt)
                    return dt.strftime("%Y-%m-%d")
                except ValueError:
                    continue
            return raw_date   # return raw if unparseable

    # Fallback: return first date anywhere in document
    match = re.search(DATE_REGEX, text, re.IGNORECASE | re.VERBOSE)
    return match.group(0).strip() if match else None


# ─────────────────────────────────────────────
# AMOUNT / CURRENCY EXTRACTION
# ─────────────────────────────────────────────

AMOUNT_REGEX = r"(?:[\$£€₹¥]?\s*[\d,]+\.?\d*)"

def extract_amount(text: str, anchor_keywords: list) -> Optional[str]:
    """
    Find a currency amount near any anchor keyword.
    Returns the amount as a string (preserves original formatting).
    """
    for kw in anchor_keywords:
        kw_match = re.search(re.escape(kw), text, re.IGNORECASE)
        if not kw_match:
            continue
        snippet = text[kw_match.end(): kw_match.end() + 100]
        amount_match = re.search(AMOUNT_REGEX, snippet)
        if amount_match:
            return amount_match.group(0).replace(",", "").strip()
    return None


def extract_all_amounts(text: str) -> List[str]:
    """Extract every currency-like amount in the document."""
    return re.findall(r"[\$£€₹¥]\s*[\d,]+\.?\d*|[\d,]+\.\d{2}", text)


# ─────────────────────────────────────────────
# TABLE / LINE ITEM EXTRACTION (Strategy D)
# ─────────────────────────────────────────────

def extract_table_rows(text: str, mode: str = "invoice") -> List[Dict[str, Any]]:
    """
    Heuristic table row extractor.
    Looks for lines containing at least 2 numeric values (amounts/quantities).

    mode: "invoice" | "bank" | "salary"
    Returns list of dicts.
    """
    rows = []
    lines = text.split("\n")

    for line in lines:
        line = line.strip()
        if not line:
            continue

        numbers = re.findall(r"[\d,]+\.?\d*", line)
        if len(numbers) < 2:
            continue

        # Attempt to split into description + values
        text_part = re.sub(r"[\d,]+\.?\d*", "", line).strip().strip("|").strip()
        text_part = clean_field(text_part)

        if mode == "bank":
            # date | description | debit | credit | balance
            date = re.search(DATE_REGEX, line, re.IGNORECASE | re.VERBOSE)
            rows.append({
                "date": date.group(0).strip() if date else None,
                "description": text_part,
                "amounts": numbers,
            })
        elif mode == "salary":
            rows.append({
                "component": text_part,
                "amount": numbers[-1] if numbers else None,
            })
        else:  # invoice line items
            rows.append({
                "description": text_part,
                "values": numbers,
            })

    return rows


# ─────────────────────────────────────────────
# GENERIC KEY-VALUE EXTRACTION
# ─────────────────────────────────────────────

def extract_all_kv(text: str) -> Dict[str, str]:
    """
    Generic key-value extractor for unknown documents.
    Looks for 'Label: Value' patterns.
    """
    kv = {}
    pattern = r"([A-Za-z][A-Za-z\s\(\)\/\-]{1,40}?)\s*[:\-]\s*(.+?)(?=\n|$)"
    matches = re.findall(pattern, text, re.MULTILINE)
    for key, value in matches:
        key = clean_field(key).lower().replace(" ", "_")
        value = clean_field(value)
        if key and value and len(key) < 60 and len(value) < 200:
            kv[key] = value
    return kv


# ─────────────────────────────────────────────
# BASIC NAMED ENTITY EXTRACTION (no spaCy)
# ─────────────────────────────────────────────

def extract_named_entities(text: str) -> Dict[str, List[str]]:
    """
    Rule-based NE extraction without spaCy.
    Detects: emails, phone numbers, URLs, postal codes, ABN/TFN patterns.
    """
    entities = {}

    emails = re.findall(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", text)
    if emails:
        entities["emails"] = list(set(emails))

    phones = re.findall(r"(?:\+?\d[\d\s\-\(\)]{7,15}\d)", text)
    if phones:
        entities["phones"] = [p.strip() for p in phones]

    urls = re.findall(r"https?://[^\s]+", text)
    if urls:
        entities["urls"] = urls

    # Currency amounts
    amounts = extract_all_amounts(text)
    if amounts:
        entities["amounts"] = amounts

    return entities


# ─────────────────────────────────────────────
# EUROPEAN AMOUNT PARSER (added for multilingual support)
# ─────────────────────────────────────────────

def parse_amount_european(value: str) -> Optional[str]:
    """
    Normalize amounts handling both European and US formatting:
      European: $3.525,00 or $35,00  → 3525.00 or 35.00
      US:       $3,525.00 or $35.00  → 3525.00 or 35.00
    """
    if not value:
        return None
    v = re.sub(r"[\$£€₹¥\s]", "", str(value)).strip()
    # European: ends with comma + 1-2 digits (e.g. "3525,00" or "35,00")
    if re.search(r",\d{1,2}$", v):
        v = v.replace(".", "").replace(",", ".")
    else:
        v = v.replace(",", "")
    try:
        f = float(v)
        return f"{f:.2f}"
    except ValueError:
        return value
