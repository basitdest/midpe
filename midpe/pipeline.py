"""
midpe/pipeline.py
MIDPE — Pipeline Orchestrator

The single function that runs the full 5-step document processing chain.
Import and call from run.py or any other script.
"""

import json
import os
import importlib
from datetime import datetime, timezone

from midpe.classification.classifier import classify_document
from midpe.extraction.strategy_selector import select_strategy
from midpe.validation.validator import validate
from midpe.confidence.scorer import score_extraction
from midpe.config import STORAGE_CONFIG


# ─────────────────────────────────────────────────────────────
# EXTRACTOR REGISTRY
# To add a new document type: add entry here + create the module
# ─────────────────────────────────────────────────────────────

EXTRACTOR_REGISTRY = {
    "invoice_extractor":  "midpe.extraction.invoice_extractor",
    "bank_extractor":     "midpe.extraction.bank_extractor",
    "po_extractor":       "midpe.extraction.po_extractor",
    "contract_extractor": "midpe.extraction.contract_extractor",
    "salary_extractor":   "midpe.extraction.salary_extractor",
    "utility_extractor":  "midpe.extraction.utility_extractor",
    "generic_extractor":  "midpe.extraction.generic_extractor",
}


def _load_extractor(name: str):
    """Dynamically import and return the extract() function for a given extractor name."""
    module_path = EXTRACTOR_REGISTRY.get(name, "midpe.extraction.generic_extractor")
    module = importlib.import_module(module_path)
    return module.extract


def _read_pdf_text(filepath: str) -> str:
    """
    Extract raw text from a PDF file.
    Tries PyMuPDF first, then pdfplumber, then Tesseract OCR.
    """
    text = ""

    # Strategy A — PyMuPDF (fastest, best for digital PDFs)
    try:
        import fitz
        doc = fitz.open(filepath)
        text = "\n".join(page.get_text() for page in doc)
        doc.close()
        if text.strip():
            return text
    except ImportError:
        pass

    # Strategy A fallback — pdfplumber
    try:
        import pdfplumber
        with pdfplumber.open(filepath) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        if text.strip():
            return text
    except ImportError:
        pass

    # Strategy B — Tesseract OCR (scanned/image PDFs)
    try:
        import pytesseract
        from pdf2image import convert_from_path
        images = convert_from_path(filepath)
        text = "\n".join(pytesseract.image_to_string(img) for img in images)
    except Exception:
        pass

    return text


def process_document(
    filepath: str = None,
    text: str = None,
    filename: str = "document.pdf",
    save_output: bool = True,
    output_dir: str = None,
) -> dict:
    """
    Run the full MIDPE pipeline on a document.

    Args:
        filepath   : Path to a PDF file on disk
        text       : Raw text string (use instead of filepath for testing)
        filename   : Override filename in metadata (auto-set if filepath given)
        save_output: Write result JSON to output_dir
        output_dir : Override the output directory from config

    Returns:
        Full structured result dict (also saved as JSON if save_output=True)
    """
    start_time = datetime.now(timezone.utc)
    log = []

    # ── Resolve input ────────────────────────────────────────
    if filepath:
        if not os.path.isfile(filepath):
            return {"error": f"File not found: {filepath}", "status": "failed"}
        filename = os.path.basename(filepath)
        log.append(f"Reading PDF: {filepath}")
        text = _read_pdf_text(filepath)

    if not text or not text.strip():
        return {
            "error": "No text could be extracted from the document. "
                     "If it is a scanned PDF, ensure Tesseract is installed.",
            "status": "failed",
            "filename": filename,
        }

    # ── Step 1: Document Classification ──────────────────────
    log.append("Step 1: Classifying document type...")
    classification = classify_document(text)
    doc_type = classification["doc_type"]
    log.append(f"  → {classification['label']} (confidence: {classification['confidence']:.2%})")

    # ── Step 2: Strategy Selection ────────────────────────────
    log.append("Step 2: Selecting extraction strategy...")
    strategy = select_strategy(text, doc_type)
    log.append(f"  → {strategy['primary']} | {strategy['reason']}")

    # ── Step 3: Field Extraction ─────────────────────────────
    extractor_name = classification["extractor"]
    log.append(f"Step 3: Extracting fields with [{extractor_name}]...")
    extract_fn = _load_extractor(extractor_name)
    extracted = extract_fn(text)
    log.append(f"  → {len(extracted)} fields returned")

    # ── Step 4a: Validation ───────────────────────────────────
    log.append("Step 4a: Validating extracted fields...")
    validation = validate(doc_type, extracted)
    log.append(f"  → Valid: {validation['is_valid']} | Errors: {len(validation['errors'])} | Warnings: {len(validation['warnings'])}")

    # ── Step 4b: Confidence Scoring ───────────────────────────
    log.append("Step 4b: Scoring confidence...")
    confidence = score_extraction(
        doc_type=doc_type,
        extracted_fields=extracted,
        classifier_confidence=classification["confidence"],
        text_quality=strategy["quality_score"],
    )
    log.append(f"  → Score: {confidence['final_score']:.2%} | Action: {confidence['storage_action'].upper()}")

    # ── Assemble Output ───────────────────────────────────────
    elapsed_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)

    result = {
        "status": "ok",
        "metadata": {
            "filename": filename,
            "filepath": filepath or "(text input)",
            "processed_at": start_time.isoformat(),
            "processing_time_ms": elapsed_ms,
            "pipeline_version": "1.0.0",
        },
        "classification": {
            "doc_type": doc_type,
            "label": classification["label"],
            "classifier_confidence": round(classification["confidence"], 4),
            "all_scores": classification["all_scores"],
        },
        "extraction_strategy": strategy,
        "extracted_data": extracted,
        "validation": validation,
        "confidence": confidence,
        "storage_action": confidence["storage_action"],
        "pipeline_log": log,
    }

    # ── Save JSON output ──────────────────────────────────────
    if save_output:
        out_dir = output_dir or STORAGE_CONFIG.get("output_dir", "output")
        os.makedirs(out_dir, exist_ok=True)
        safe_name = os.path.splitext(filename)[0].replace(" ", "_")
        out_path = os.path.join(out_dir, f"{safe_name}_result.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, default=str)
        result["_saved_to"] = out_path
        log.append(f"  → Saved to: {out_path}")

    return result