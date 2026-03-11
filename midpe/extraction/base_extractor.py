"""
extraction/bank_extractor.py
Bank Statement field extractor.
"""

import re
from extraction.base_extractor import (
    find_near_keyword, extract_date, extract_amount,
    extract_table_rows, clean_field
)


def extract(text: str) -> dict:
    result = {
        "account_number": None,
        "account_holder": None,
        "bank_name": None,
        "statement_period": None,
        "opening_balance": None,
        "closing_balance": None,
        "transactions": [],
        "_raw_text_length": len(text),
    }

    # Account number
    acc_match = re.search(
        r"account\s*(?:number|no\.?|#)\s*[:\-]?\s*([X\d\s\-]+)",
        text, re.IGNORECASE
    )
    if acc_match:
        result["account_number"] = clean_field(acc_match.group(1))

    # Account holder
    result["account_holder"] = find_near_keyword(
        text, ["account holder", "account name", "customer name", "name"]
    )

    # Bank name — look for "Bank" following a capitalized word in the header
    bank_match = re.search(r"([A-Z][a-zA-Z\s]+(?:Bank|Banking|Financial))", text)
    if bank_match:
        result["bank_name"] = clean_field(bank_match.group(1))

    # Statement period
    period_match = re.search(
        r"statement\s+period\s*[:\-]?\s*(.+?)(?:\n|$)",
        text, re.IGNORECASE
    )
    if period_match:
        result["statement_period"] = clean_field(period_match.group(1))

    # Balances
    result["opening_balance"] = extract_amount(text, ["opening balance", "beginning balance", "balance brought forward"])
    result["closing_balance"] = extract_amount(text, ["closing balance", "ending balance", "balance carried forward", "available balance"])

    # Transactions (table rows)
    result["transactions"] = extract_table_rows(text, mode="bank")

    return result