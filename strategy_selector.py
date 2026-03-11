"""
extraction/strategy_selector.py
Extraction Strategy Selector — Step 2 of MIDPE pipeline.

Decides which extraction strategy to apply based on:
  - Whether the PDF has a text layer (Strategy A)
  - Whether text is absent/garbled (Strategy B — OCR)
  - Whether layout anchoring is better (Strategy C)
  - Whether tables are present (Strategy D)
"""

import re


# ─────────────────────────────────────────────
# TEXT QUALITY CHECKS
# ─────────────────────────────────────────────

def has_text_layer(raw_text: str, min_chars: int = 100) -> bool:
    """Returns True if the extracted text has enough content."""
    cleaned = raw_text.strip()
    return len(cleaned) >= min_chars


def text_quality_score(raw_text: str) -> float:
    """
    Score text layer quality 0–1.
    Penalizes garbled/OCR noise characters.
    """
    if not raw_text:
        return 0.0
    total = len(raw_text)
    readable = len(re.findall(r"[a-zA-Z0-9 ,.\-:/$%@\n]", raw_text))
    return readable / total


def has_tables(raw_text: str) -> bool:
    """
    Heuristic: multiple lines with consistent numeric columns suggest a table.
    """
    lines = [l.strip() for l in raw_text.split("\n") if l.strip()]
    numeric_lines = sum(1 for l in lines if len(re.findall(r"\d+[\.,]\d+", l)) >= 2)
    return numeric_lines >= 3


# ─────────────────────────────────────────────
# STRATEGY SELECTOR
# ─────────────────────────────────────────────

def select_strategy(raw_text: str, doc_type: str) -> dict:
    """
    Given raw extracted text (from a PDF reader) and document type,
    return the recommended extraction strategy.

    Returns:
        {
            "primary": str,       # strategy key
            "secondary": str,     # fallback strategy
            "use_tables": bool,
            "reason": str,
        }
    """
    quality = text_quality_score(raw_text)
    has_text = has_text_layer(raw_text)
    tables_present = has_tables(raw_text)

    # Document types that almost always have tables
    table_heavy_types = {"bank_statement", "invoice", "purchase_order", "salary_slip"}

    if has_text and quality >= 0.75:
        primary = "strategy_a"   # Direct text layer
        reason = f"Good text layer detected (quality={quality:.0%})"
    elif has_text and quality >= 0.40:
        primary = "strategy_c"   # Layout anchoring (partial text)
        reason = f"Partial text layer (quality={quality:.0%}), using layout anchoring"
    else:
        primary = "strategy_b"   # OCR fallback
        reason = f"No usable text layer (quality={quality:.0%}), switching to OCR"

    use_tables = tables_present or doc_type in table_heavy_types
    secondary = "strategy_d" if use_tables else "strategy_c"

    return {
        "primary": primary,
        "secondary": secondary,
        "use_tables": use_tables,
        "quality_score": round(quality, 3),
        "reason": reason,
    }


# ─────────────────────────────────────────────
# CLI TEST
# ─────────────────────────────────────────────
if __name__ == "__main__":
    sample_text = """
    Invoice Number: INV-2024-0042
    Date: 01/04/2024
    Item          Qty    Unit Price    Total
    Dev Services   1      5000.00      5000.00
    GST (10%)                          500.00
    Total                             5500.00
    """
    result = select_strategy(sample_text, "invoice")
    print(f"Primary strategy : {result['primary']}")
    print(f"Use table detect : {result['use_tables']}")
    print(f"Reason           : {result['reason']}")