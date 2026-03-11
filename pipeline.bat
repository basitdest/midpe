cat > /home/claude/midpe/pipeline.py << 'PYEOF'
"""
pipeline.py — MIDPE Main Pipeline Orchestrator
Ties together all 5 steps of the document processing engine.

Usage:
    from pipeline import process_document
    result = process_document(text="...", filename="invoice.pdf")
"""

import json, os, sys, importlib
from datetime import datetime
sys.path.insert(0, os.path.dirname(__file__))

from classification.classifier import classify_document
from extraction.strategy_selector import select_strategy
from validation.validator import validate
from confidence.scorer import score_extraction
from config import STORAGE_CONFIG


def _load_extractor(name: str):
    extractors = {
        "invoice_extractor":  "extraction.invoice_extractor",
        "bank_extractor":     "extraction.bank_extractor",
        "po_extractor":       "extraction.po_extractor",
        "contract_extractor": "extraction.contract_extractor",
        "salary_extractor":   "extraction.salary_extractor",
        "utility_extractor":  "extraction.utility_extractor",
        "generic_extractor":  "extraction.generic_extractor",
    }
    module = importlib.import_module(extractors.get(name, "extraction.generic_extractor"))
    return module.extract


def process_document(text=None, filepath=None, filename="unknown.pdf", save_output=True):
    start_time = datetime.utcnow()
    log = []

    if text is None and filepath:
        text = _read_pdf_text(filepath)
        filename = os.path.basename(filepath)

    if not text or not text.strip():
        return {"error": "No text extracted.", "status": "failed"}

    # Step 1 - Classification
    log.append("Step 1: Classifying document...")
    classification = classify_document(text)
    doc_type = classification["doc_type"]

    # Step 2 - Strategy
    log.append("Step 2: Selecting strategy...")
    strategy = select_strategy(text, doc_type)

    # Step 3 - Extraction
    log.append(f"Step 3: Extracting [{classification['extractor']}]...")
    extracted = _load_extractor(classification["extractor"])(text)

    # Step 4a - Validation
    log.append("Step 4a: Validating...")
    validation = validate(doc_type, extracted)

    # Step 4b - Confidence
    log.append("Step 4b: Scoring confidence...")
    confidence = score_extraction(doc_type, extracted, classification["confidence"], strategy["quality_score"])

    elapsed_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)

    output = {
        "metadata": {"filename": filename, "processed_at": start_time.isoformat() + "Z", "processing_time_ms": elapsed_ms, "pipeline_version": "1.0.0"},
        "classification": {"doc_type": doc_type, "label": classification["label"], "classifier_confidence": classification["confidence"], "all_scores": classification["all_scores"]},
        "strategy": strategy,
        "extracted_data": extracted,
        "validation": validation,
        "confidence": confidence,
        "storage_action": confidence["storage_action"],
        "pipeline_log": log,
    }

    if save_output and STORAGE_CONFIG.get("save_json"):
        os.makedirs(STORAGE_CONFIG["output_dir"], exist_ok=True)
        out_path = os.path.join(STORAGE_CONFIG["output_dir"], f"{filename.replace('.pdf','')}_result.json")
        with open(out_path, "w") as f:
            json.dump(output, f, indent=2, default=str)
        output["_saved_to"] = out_path

    return output


def _read_pdf_text(filepath):
    text = ""
    try:
        import fitz
        doc = fitz.open(filepath)
        text = "\n".join(p.get_text() for p in doc)
        doc.close()
        if text.strip(): return text
    except ImportError: pass
    try:
        import pdfplumber
        with pdfplumber.open(filepath) as pdf:
            text = "\n".join(p.extract_text() or "" for p in pdf.pages)
        if text.strip(): return text
    except ImportError: pass
    return text


if __name__ == "__main__":
    demo_text = """
    TAX INVOICE
    Invoice Number: INV-2024-00847
    Invoice Date: 15/03/2024
    Due Date: 14/04/2024
    From: Nexus Tech Solutions Pty Ltd
    Bill To: Meridian Consulting Group
    Description                   Qty    Unit Price      Amount
    Cloud Infrastructure Setup     1      4500.00     4500.00
    API Integration Services       3       800.00     2400.00
    Technical Documentation        1       600.00      600.00
    Subtotal:                                         7500.00
    GST (10%):                                         750.00
    Total Amount Due:                                 8250.00
    Payment Terms: Net 30
    """
    result = process_document(text=demo_text, filename="demo_invoice.pdf", save_output=False)
    print(f"\nDocument Type  : {result['classification']['label']}")
    print(f"Confidence     : {result['classification']['classifier_confidence']:.2%}")
    print(f"Storage Action : {result['storage_action'].upper()}")
    print(f"Processing     : {result['metadata']['processing_time_ms']}ms")
    print("\nExtracted:")
    for k,v in result["extracted_data"].items():
        if v and not k.startswith("_") and k not in ("line_items","transactions","earnings"):
            print(f"  {k:25s}: {v}")
PYEOF
echo "done"