"""
confidence/scorer.py
Confidence Scoring Engine — Step 4 of MIDPE pipeline.

Produces a confidence score (0–1) for the extracted output based on:
  1. Keyword match ratio (from classifier)
  2. Required fields present
  3. Field format validation
  4. Text layer quality

Also determines storage action: "verified" | "needs_review" | "unverified" | "rejected"
"""

from midpe.config import CONFIDENCE_CONFIG, VALIDATION_RULES


def score_extraction(
    doc_type: str,
    extracted_fields: dict,
    classifier_confidence: float,
    text_quality: float = 1.0,
) -> dict:
    """
    Score an extraction result.

    Args:
        doc_type: Detected document type key
        extracted_fields: Dict of extracted field values
        classifier_confidence: Score from Step 1 (0–1)
        text_quality: Score from strategy selector (0–1)

    Returns:
        {
            "final_score": float,
            "storage_action": str,
            "breakdown": dict,
            "missing_fields": list,
        }
    """
    weights = CONFIDENCE_CONFIG["scoring_weights"]
    rules = VALIDATION_RULES.get(doc_type, {})
    required_fields = rules.get("required_fields", [])

    # ── Component 1: Keyword / classifier confidence ─────────
    keyword_component = classifier_confidence * weights["keyword_match"]

    # ── Component 2: Required fields present ─────────────────
    if required_fields:
        present = [f for f in required_fields if extracted_fields.get(f)]
        fields_ratio = len(present) / len(required_fields)
        missing_fields = [f for f in required_fields if not extracted_fields.get(f)]
    else:
        fields_ratio = 1.0
        missing_fields = []
    fields_component = fields_ratio * weights["required_fields_present"]

    # ── Component 3: Field format validity ───────────────────
    format_score = _check_format_validity(doc_type, extracted_fields, rules)
    format_component = format_score * weights["field_format_valid"]

    # ── Component 4: Text layer quality ──────────────────────
    quality_component = text_quality * weights["text_layer_quality"]

    # ── Final score ───────────────────────────────────────────
    final_score = keyword_component + fields_component + format_component + quality_component
    final_score = round(min(final_score, 1.0), 4)

    # ── Storage decision ──────────────────────────────────────
    high  = CONFIDENCE_CONFIG["high_threshold"]
    med   = CONFIDENCE_CONFIG["medium_threshold"]
    low   = CONFIDENCE_CONFIG["low_threshold"]

    if final_score >= high:
        storage_action = "verified"
    elif final_score >= med:
        storage_action = "needs_review"
    elif final_score >= low:
        storage_action = "unverified"
    else:
        storage_action = "rejected"

    return {
        "final_score": final_score,
        "storage_action": storage_action,
        "breakdown": {
            "keyword_match":           round(keyword_component, 4),
            "required_fields_present": round(fields_component, 4),
            "field_format_valid":      round(format_component, 4),
            "text_layer_quality":      round(quality_component, 4),
        },
        "missing_fields": missing_fields,
        "fields_found_ratio": round(fields_ratio, 3),
    }


def _check_format_validity(doc_type: str, fields: dict, rules: dict) -> float:
    """
    Check individual field formats. Returns ratio of fields that look valid.
    """
    checks = []

    # Amount fields: should be numeric
    amount_keys = [k for k in fields if "amount" in k or "salary" in k or "balance" in k or "total" in k]
    for k in amount_keys:
        val = fields.get(k)
        if val:
            import re
            checks.append(bool(re.search(r"[\d]+", str(val))))

    # Date fields: should not be None if required
    date_keys = [k for k in fields if "date" in k or "period" in k]
    for k in date_keys:
        val = fields.get(k)
        checks.append(val is not None)

    # ID / number fields: should be alphanumeric
    id_keys = [k for k in fields if "number" in k or "_id" in k or "_no" in k]
    for k in id_keys:
        val = fields.get(k)
        if val:
            import re
            checks.append(bool(re.search(r"[A-Z0-9]", str(val).upper())))

    if not checks:
        return 0.75   # assume reasonable if no checkable fields
    return sum(checks) / len(checks)
