"""
midpe/pipeline.py
MIDPE — Pipeline Orchestrator
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
    module_path = EXTRACTOR_REGISTRY.get(name, "midpe.extraction.generic_extractor")
    module = importlib.import_module(module_path)
    return module.extract


def _read_pdf_text(filepath: str) -> str:
    """
    Extract raw text from a PDF.
    Tries PyMuPDF → pdfplumber → Tesseract OCR in order.
    Raises RuntimeError with a clear message if the file cannot be read.
    """
    text = ""

    # Strategy A — PyMuPDF
    try:
        import fitz
        doc = fitz.open(filepath)
        text = "\n".join(page.get_text() for page in doc)
        doc.close()
        if text.strip():
            return text
    except ImportError:
        pass  # not installed, try next
    except Exception as e:
        raise RuntimeError(f"PyMuPDF failed to open the file: {e}") from e

    # Strategy A fallback — pdfplumber
    try:
        import pdfplumber
        with pdfplumber.open(filepath) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        if text.strip():
            return text
    except ImportError:
        pass  # not installed, try next
    except Exception as e:
        raise RuntimeError(f"pdfplumber failed to open the file: {e}") from e

    # Strategy B — Tesseract OCR (scanned/image PDFs only)
    try:
        import pytesseract
        from pdf2image import convert_from_path
        images = convert_from_path(filepath)
        text = "\n".join(pytesseract.image_to_string(img) for img in images)
        if text.strip():
            return text
    except ImportError:
        pass  # pdf2image or pytesseract not installed
    except Exception as e:
        raise RuntimeError(f"OCR failed: {e}") from e

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
        filename   : Override filename in metadata
        save_output: Write result JSON to output_dir
        output_dir : Override the output directory from config
    """
    start_time = datetime.now(timezone.utc)
    log = []

    # ── Resolve input ─────────────────────────────────────────
    if filepath:
        if not os.path.isfile(filepath):
            return {
                "error": f"File not found: '{filepath}'. Check the path is correct.",
                "status": "failed",
                "filename": os.path.basename(filepath),
            }
        filename = os.path.basename(filepath)
        log.append(f"Reading PDF: {filepath}")
        try:
            text = _read_pdf_text(filepath)
        except RuntimeError as e:
            return {
                "error": str(e),
                "status": "failed",
                "filename": filename,
            }

    if not text or not text.strip():
        # Diagnose why no text was extracted
        libs = []
        try:
            import fitz
            libs.append("PyMuPDF")
        except ImportError:
            pass
        try:
            import pdfplumber
            libs.append("pdfplumber")
        except ImportError:
            pass

        if not libs:
            msg = (
                "No PDF library is installed. "
                "Run:  pip install pdfplumber"
            )
        else:
            msg = (
                f"No text could be extracted (tried: {', '.join(libs)}). "
                "The PDF may be a scanned image — install Tesseract + pdf2image for OCR support, "
                "or verify the file is a valid PDF and not empty or password-protected."
            )
        return {"error": msg, "status": "failed", "filename": filename}

    # ── Step 1: Classification ────────────────────────────────
    log.append("Step 1: Classifying document type...")
    classification = classify_document(text)
    doc_type = classification["doc_type"]
    log.append(f"  → {classification['label']} (confidence: {classification['confidence']:.2%})")

    # ── Step 2: Strategy Selection ────────────────────────────
    log.append("Step 2: Selecting extraction strategy...")
    strategy = select_strategy(text, doc_type)
    log.append(f"  → {strategy['primary']} | {strategy['reason']}")

    # ── Step 3: Field Extraction ──────────────────────────────
    extractor_name = classification["extractor"]
    log.append(f"Step 3: Extracting fields [{extractor_name}]...")
    extract_fn = _load_extractor(extractor_name)
    extracted = extract_fn(text)
    log.append(f"  → {len(extracted)} fields returned")

    # ── Step 4a: Validation ───────────────────────────────────
    log.append("Step 4a: Validating fields...")
    validation = validate(doc_type, extracted)
    log.append(f"  → Valid: {validation['is_valid']} | Errors: {len(validation['errors'])}")

    # ── Step 4b: Confidence Scoring ───────────────────────────
    log.append("Step 4b: Scoring confidence...")
    confidence = score_extraction(
        doc_type=doc_type,
        extracted_fields=extracted,
        classifier_confidence=classification["confidence"],
        text_quality=strategy["quality_score"],
    )
    log.append(f"  → Score: {confidence['final_score']:.2%} | Action: {confidence['storage_action'].upper()}")

    # ── Assemble output ───────────────────────────────────────
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

    # ── Save JSON ─────────────────────────────────────────────
    if save_output:
        out_dir = output_dir or STORAGE_CONFIG.get("output_dir", "output")
        os.makedirs(out_dir, exist_ok=True)
        safe_name = os.path.splitext(filename)[0].replace(" ", "_")
        out_path = os.path.join(out_dir, f"{safe_name}_result.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, default=str)
        result["_saved_to"] = out_path

    return result
