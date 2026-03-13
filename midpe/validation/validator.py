"""
validation/validator.py
Validation Engine — validates extracted fields against configurable rules.
"""

import re
from datetime import datetime
from midpe.config import VALIDATION_RULES


def validate(doc_type: str, extracted: dict) -> dict:
    rules = VALIDATION_RULES.get(doc_type, {})
    errors, warnings, flagged = [], [], []

    # Required fields
    for field in rules.get("required_fields", []):
        if not extracted.get(field):
            errors.append(f"Missing required field: '{field}'")
            flagged.append(field)

    # Amount positivity
    if rules.get("amount_must_be_positive"):
        for k in [k for k in extracted if "amount" in k or "total" in k or "salary" in k]:
            val = extracted.get(k)
            if val:
                num = _parse_number(val)
                if num is not None and num <= 0:
                    errors.append(f"Amount field '{k}' must be positive, got: {val}")
                    flagged.append(k)

    # Net < Gross (salary)
    if rules.get("net_must_be_less_than_gross"):
        net   = _parse_number(extracted.get("net_salary"))
        gross = _parse_number(extracted.get("gross_salary"))
        if net is not None and gross is not None and net > gross:
            errors.append(f"Net salary ({net}) cannot exceed gross ({gross})")

    # Date format
    for k in [k for k in extracted if "date" in k or "period" in k]:
        val = extracted.get(k)
        if val and rules.get("date_format") and not _is_valid_date(val, rules["date_format"]):
            warnings.append(f"Field '{k}' has unexpected date format: '{val}'")

    # Balance check
    if rules.get("balance_check"):
        closing = _parse_number(extracted.get("closing_balance"))
        if closing is not None and closing < 0:
            warnings.append("Closing balance is negative")

    return {"is_valid": len(errors) == 0, "errors": errors, "warnings": warnings, "flagged_fields": flagged}


def _parse_number(value):
    if value is None:
        return None
    try:
        return float(re.sub(r"[,$£€\s]", "", str(value)))
    except ValueError:
        return None


def _is_valid_date(value, formats):
    for fmt in formats:
        try:
            datetime.strptime(str(value), fmt)
            return True
        except ValueError:
            continue
    return False
