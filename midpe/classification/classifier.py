"""
classification/classifier.py
Document Type Classifier — Step 1 of MIDPE pipeline.

Methods used:
  1. Keyword frequency scoring
  2. Header/regex pattern matching
  3. TF-IDF + Logistic Regression (optional, loads if model exists)

Returns: (doc_type: str, confidence: float, scores: dict)
"""

import re
import math
from collections import Counter
from config import DOCUMENT_TYPES


# ─────────────────────────────────────────────
# UTILITIES
# ─────────────────────────────────────────────

def normalize_text(text: str) -> str:
    """Lowercase, collapse whitespace."""
    return re.sub(r"\s+", " ", text.lower().strip())


def extract_header_region(text: str, lines: int = 15) -> str:
    """Return the top N lines of the document (header area)."""
    return "\n".join(text.split("\n")[:lines])


# ─────────────────────────────────────────────
# STEP 1A — KEYWORD FREQUENCY SCORING
# ─────────────────────────────────────────────

def keyword_score(text: str, doc_type_key: str) -> float:
    """
    Score a document against a doc_type's keyword list.
    Returns a normalized score between 0 and 1.
    """
    normalized = normalize_text(text)
    keywords = DOCUMENT_TYPES[doc_type_key]["keywords"]
    matched = sum(1 for kw in keywords if kw in normalized)
    return matched / len(keywords) if keywords else 0.0


# ─────────────────────────────────────────────
# STEP 1B — HEADER PATTERN MATCHING
# ─────────────────────────────────────────────

def header_pattern_score(text: str, doc_type_key: str) -> float:
    """
    Regex match on the header region.
    Returns 1.0 if any pattern matches, else 0.0.
    """
    header = normalize_text(extract_header_region(text))
    patterns = DOCUMENT_TYPES[doc_type_key].get("header_patterns", [])
    for pattern in patterns:
        if re.search(pattern, header):
            return 1.0
    return 0.0


# ─────────────────────────────────────────────
# STEP 1C — OPTIONAL TF-IDF SCORING (stub)
# ─────────────────────────────────────────────

def tfidf_score(text: str, doc_type_key: str) -> float:
    """
    Lightweight TF-IDF approximation using the keyword list as a vocabulary.
    No external model needed. Returns a score between 0 and 1.
    """
    normalized = normalize_text(text)
    words = normalized.split()
    word_counts = Counter(words)
    total_words = len(words) if words else 1

    keywords = DOCUMENT_TYPES[doc_type_key]["keywords"]
    score = 0.0
    for kw in keywords:
        kw_words = kw.split()
        # TF: frequency of keyword phrase
        tf = sum(word_counts.get(w, 0) for w in kw_words) / total_words
        # IDF approximation: rarer keywords across doc types get higher weight
        appearances_in_other_types = sum(
            1 for other_key, other_cfg in DOCUMENT_TYPES.items()
            if other_key != doc_type_key and kw in other_cfg["keywords"]
        )
        idf = math.log(len(DOCUMENT_TYPES) / (1 + appearances_in_other_types))
        score += tf * idf

    # Normalize to 0–1 range
    return min(score / max(len(keywords), 1), 1.0)


# ─────────────────────────────────────────────
# MAIN CLASSIFIER
# ─────────────────────────────────────────────

def classify_document(text: str) -> dict:
    """
    Classify a document using keyword, header pattern, and TF-IDF scoring.

    Returns:
        {
            "doc_type": str,
            "label": str,
            "confidence": float,       # combined score 0–1
            "all_scores": {doc_type: score, ...},
            "extractor": str,
        }
    """
    all_scores = {}

    for doc_type_key, cfg in DOCUMENT_TYPES.items():
        kw   = keyword_score(text, doc_type_key)          # weight: 0.40
        hdr  = header_pattern_score(text, doc_type_key)   # weight: 0.40
        tfidf = tfidf_score(text, doc_type_key)           # weight: 0.20

        # Priority modifier: lower priority = slight penalty
        priority_weight = 1.0 / cfg.get("priority", 1)

        combined = (kw * 0.40 + hdr * 0.40 + tfidf * 0.20) * priority_weight
        all_scores[doc_type_key] = round(combined, 4)

    # Best match
    best_type = max(all_scores, key=all_scores.get)
    best_score = all_scores[best_type]

    # Fallback if confidence is too low
    if best_score < 0.05:
        best_type = "unknown"
        label = "Unknown / Generic"
        extractor = "generic_extractor"
    else:
        label = DOCUMENT_TYPES[best_type]["label"]
        extractor = DOCUMENT_TYPES[best_type]["extractor"]

    return {
        "doc_type": best_type,
        "label": label,
        "confidence": best_score,
        "all_scores": all_scores,
        "extractor": extractor,
    }


# ─────────────────────────────────────────────
# CLI TEST
# ─────────────────────────────────────────────
if __name__ == "__main__":
    sample = """
    TAX INVOICE
    Invoice Number: INV-2024-00123
    Invoice Date: 15/03/2024
    Bill To: ABC Corp Ltd.
    Item Description: Software Development Services
    Quantity: 1   Unit Price: $8,500.00
    Subtotal: $8,500.00
    GST (10%): $850.00
    Total Amount Due: $9,350.00
    Payment Terms: Net 30
    """
    result = classify_document(sample)
    print(f"Classified as: {result['label']} (confidence: {result['confidence']:.2%})")
    print(f"Extractor: {result['extractor']}")
    print("\nAll scores:")
    for k, v in sorted(result['all_scores'].items(), key=lambda x: -x[1]):
        print(f"  {k:20s}: {v:.4f}")