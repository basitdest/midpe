"""
extraction/contract_extractor.py
Contract field extractor.
"""
import re
from midpe.extraction.base_extractor import find_near_keyword, extract_date, clean_field


def extract(text: str) -> dict:
    result = {
        "contract_title": None,
        "parties": [],
        "effective_date": None,
        "termination_date": None,
        "governing_law": None,
        "contract_value": None,
        "key_clauses": [],
        "_raw_text_length": len(text),
    }

    # Title: first meaningful line
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    if lines:
        result["contract_title"] = lines[0][:120]

    # Parties — common patterns
    party_matches = re.findall(
        r"(?:between|party\s+[A-Z]|parties)\s*[:\-]?\s*\"?([A-Z][A-Za-z\s,\.]+?)\"?\s+(?:and|,|\n)",
        text, re.IGNORECASE
    )
    result["parties"] = [clean_field(p) for p in party_matches[:4]]

    result["effective_date"]    = extract_date(text, ["effective date", "commencement date", "start date", "dated"])
    result["termination_date"]  = extract_date(text, ["termination date", "expiry date", "end date", "expires on"])

    gov_match = re.search(r"governing\s+law\s*[:\-]?\s*(.+?)(?:\n|\.)", text, re.IGNORECASE)
    if gov_match:
        result["governing_law"] = clean_field(gov_match.group(1))

    # Key clause detection
    clause_keywords = [
        "confidentiality", "indemnification", "limitation of liability",
        "intellectual property", "force majeure", "non-compete",
        "dispute resolution", "termination"
    ]
    result["key_clauses"] = [kw for kw in clause_keywords if kw.lower() in text.lower()]

    return result