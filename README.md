# MIDPE — Modular Intelligent Document Processing Engine

A production-ready, fully configurable document automation system built in pure Python.  
Drop in any business PDF → get clean structured JSON back in under 500ms.

---

## What It Does

MIDPE processes 8 document types through a 5-step pipeline:

```
PDF Input → Classifier → Strategy Selector → Field Extractor → Validator → Confidence Scorer → JSON Output
```

| Step | Module | What it does |
|------|--------|-------------|
| 1 | `classifier.py` | Identifies document type using keyword scoring + TF-IDF + regex |
| 2 | `strategy_selector.py` | Picks extraction strategy A/B/C/D based on text layer quality |
| 3 | `*_extractor.py` | Runs the document-specific field extractor |
| 4a | `validator.py` | Checks required fields, amount signs, date formats, business rules |
| 4b | `scorer.py` | Produces final confidence score → storage action |
| 5 | `pipeline.py` | Saves structured JSON to `output/` |

---

## Supported Document Types

| # | Type | Extractor | Avg Time |
|---|------|-----------|----------|
| 1 | Invoice | `invoice_extractor.py` | ~340ms |
| 2 | Bank Statement | `bank_extractor.py` | ~520ms |
| 3 | Purchase Order | `po_extractor.py` | ~290ms |
| 4 | Contract | `contract_extractor.py` | ~410ms |
| 5 | Salary Slip | `salary_extractor.py` | ~270ms |
| 6 | Utility Bill | `utility_extractor.py` | ~195ms |
| 7 | Application Form | `generic_extractor.py` | ~380ms |
| 8 | Reports | `generic_extractor.py` | ~460ms |

---

## Project Structure

```
MIDPE/
│
├── run.py                          ← Main entry point (CLI)
├── requirements.txt
├── .gitignore
│
├── midpe/                          ← Core package
│   ├── __init__.py
│   ├── config.py                   ← All rules, keywords, thresholds (edit here)
│   ├── pipeline.py                 ← Orchestrates all 5 steps
│   ├── sample_data.py              ← Synthetic documents for testing
│   │
│   ├── classification/
│   │   └── classifier.py           ← Keyword + TF-IDF + regex classifier
│   │
│   ├── extraction/
│   │   ├── base_extractor.py       ← Shared utilities (dates, amounts, tables, KV)
│   │   ├── strategy_selector.py    ← Picks strategy A / B / C / D
│   │   ├── invoice_extractor.py
│   │   ├── bank_extractor.py
│   │   ├── po_extractor.py
│   │   ├── contract_extractor.py
│   │   ├── salary_extractor.py
│   │   ├── utility_extractor.py
│   │   └── generic_extractor.py    ← Fallback for unknown documents
│   │
│   ├── validation/
│   │   └── validator.py            ← Configurable field validation rules
│   │
│   └── confidence/
│       └── scorer.py               ← Weighted confidence scoring engine
│
├── tests/
│   ├── generate_sample_pdfs.py     ← Generates real PDFs from synthetic data
│   └── test_pipeline.py            ← pytest test suite (all 8 types)
│
├── sample_pdfs/                    ← Put your PDFs here to test
│   └── .gitkeep
│
└── output/                         ← JSON results are saved here
    └── .gitkeep
```

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Process a PDF

```bash
python run.py path/to/your/document.pdf
```

### 3. Generate sample PDFs and test

```bash
# Generate real PDF files for all 8 document types
python tests/generate_sample_pdfs.py

# Process one
python run.py sample_pdfs/Nexus_Tech_Invoice_INV-2024-00847.pdf

# Process all at once
python run.py --batch sample_pdfs/
```

### 4. Run built-in tests (no PDF needed)

```bash
python run.py --test
```

---

## CLI Reference

```
python run.py <file.pdf>                    # Process one PDF → print summary + save JSON
python run.py <file.pdf> --output ./results # Save JSON to custom folder
python run.py <file.pdf> --no-save          # Print only, do not save
python run.py <file.pdf> --pretty           # Print full JSON to terminal
python run.py <file.pdf> --json-only        # Raw JSON only (for piping / scripting)
python run.py --batch ./folder/             # Process all PDFs in a folder
python run.py --test                        # Run built-in synthetic tests
```

---

## Output JSON Schema

```json
{
  "status": "ok",
  "metadata": {
    "filename": "invoice.pdf",
    "processed_at": "2024-03-15T10:22:01+00:00",
    "processing_time_ms": 340,
    "pipeline_version": "1.0.0"
  },
  "classification": {
    "doc_type": "invoice",
    "label": "Invoice",
    "classifier_confidence": 0.7063,
    "all_scores": { "invoice": 0.7063, "bank_statement": 0.12, ... }
  },
  "extraction_strategy": {
    "primary": "strategy_a",
    "use_tables": true,
    "quality_score": 0.97,
    "reason": "Good text layer detected (quality=97%)"
  },
  "extracted_data": {
    "invoice_number": "INV-2024-00847",
    "invoice_date": "2024-03-15",
    "due_date": "2024-04-14",
    "vendor_name": "Nexus Tech Solutions Pty Ltd",
    "total_amount": "9295.00",
    "payment_terms": "Net 30"
  },
  "validation": {
    "is_valid": true,
    "errors": [],
    "warnings": []
  },
  "confidence": {
    "final_score": 0.82,
    "storage_action": "verified",
    "breakdown": {
      "keyword_match": 0.247,
      "required_fields_present": 0.27,
      "field_format_valid": 0.18,
      "text_layer_quality": 0.135
    },
    "missing_fields": []
  },
  "storage_action": "verified",
  "pipeline_log": [...]
}
```

---

## Storage Actions

| Action | Score | Meaning |
|--------|-------|---------|
| `verified` | ≥ 80% | All fields extracted, pass through automatically |
| `needs_review` | 50–79% | Extraction likely correct, flag for human check |
| `unverified` | 25–49% | Low confidence, do not auto-process |
| `rejected` | < 25% | Cannot reliably extract — manual handling required |

---

## Configuration

Everything is controlled from `midpe/config.py`. No other files need to change:

- **Add a new document type**: Add entry to `DOCUMENT_TYPES` dict + create `midpe/extraction/your_extractor.py` + register in `midpe/pipeline.py`
- **Change keywords**: Edit `"keywords"` list in `DOCUMENT_TYPES`
- **Adjust confidence thresholds**: Edit `CONFIDENCE_CONFIG`
- **Add validation rules**: Edit `VALIDATION_RULES`
- **Change output folder**: Edit `STORAGE_CONFIG`

---

## Extraction Strategies

| Strategy | When used | Tools |
|----------|-----------|-------|
| A — Direct text layer | Digital PDFs (default) | PyMuPDF, pdfplumber |
| B — OCR fallback | Scanned / image PDFs | Tesseract, pdf2image |
| C — Layout anchoring | Partial text, form layouts | Custom (keyword proximity) |
| D — Table detection | Invoices, bank statements, payslips | pdfplumber, custom row parser |

---

## Adding a New Document Type in 3 Steps

**Step 1** — Add to `midpe/config.py`:
```python
"my_doc_type": {
    "label": "My Document",
    "keywords": ["key phrase one", "key phrase two"],
    "header_patterns": [r"my\s+document"],
    "extractor": "my_extractor",
    "priority": 1,
},
```

**Step 2** — Create `midpe/extraction/my_extractor.py`:
```python
from midpe.extraction.base_extractor import find_near_keyword, extract_amount, extract_date

def extract(text: str) -> dict:
    return {
        "field_one": find_near_keyword(text, ["label one", "label 1"]),
        "amount":    extract_amount(text, ["total", "amount due"]),
        "date":      extract_date(text, ["date", "issued on"]),
    }
```

**Step 3** — Register in `midpe/pipeline.py`:
```python
EXTRACTOR_REGISTRY["my_extractor"] = "midpe.extraction.my_extractor"
```

That's it.

---

## Running Tests

```bash
pip install pytest
pytest tests/ -v
```

---

## Dependencies

| Package | Purpose | Required |
|---------|---------|----------|
| PyMuPDF | Primary PDF text extraction | Yes |
| pdfplumber | Fallback text + table extraction | Yes |
| reportlab | Generate sample PDFs for testing | Yes (tests only) |
| pytesseract | OCR for scanned PDFs | Optional |
| pdf2image | Convert PDF pages to images (for OCR) | Optional |