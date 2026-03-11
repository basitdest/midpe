"""
MIDPE – Modular Intelligent Document Processing Engine
config.py — Central configuration: document types, keywords, validation rules,
             confidence thresholds, and extraction strategies. All editable here.
"""

# ─────────────────────────────────────────────
# 1. DOCUMENT TYPE DEFINITIONS
# ─────────────────────────────────────────────
DOCUMENT_TYPES = {
    "invoice": {
        "label": "Invoice",
        "keywords": [
            "invoice number", "invoice no", "bill to", "tax invoice",
            "invoice date", "due date", "subtotal", "tax amount",
            "total amount due", "payment terms", "item description",
            "unit price", "quantity", "gst", "vat", "amount due"
        ],
        "header_patterns": [r"invoice\s*#?\s*\d+", r"tax\s+invoice", r"bill\s+to"],
        "extractor": "invoice_extractor",
        "priority": 1,
    },
    "bank_statement": {
        "label": "Bank Statement",
        "keywords": [
            "statement period", "account number", "account holder",
            "opening balance", "closing balance", "credit", "debit",
            "transaction date", "bank name", "branch", "ifsc", "swift",
            "available balance", "statement date"
        ],
        "header_patterns": [r"bank\s+statement", r"account\s+statement", r"statement\s+of\s+account"],
        "extractor": "bank_extractor",
        "priority": 1,
    },
    "purchase_order": {
        "label": "Purchase Order",
        "keywords": [
            "purchase order", "po number", "po date", "vendor",
            "ship to", "bill to", "delivery date", "order total",
            "item code", "quantity ordered", "unit cost", "approved by"
        ],
        "header_patterns": [r"purchase\s+order", r"p\.?o\.?\s+#?\s*\d+"],
        "extractor": "po_extractor",
        "priority": 1,
    },
    "contract": {
        "label": "Contract",
        "keywords": [
            "agreement", "parties", "terms and conditions", "effective date",
            "termination", "governing law", "confidentiality", "jurisdiction",
            "whereas", "hereinafter", "indemnification", "liability",
            "intellectual property", "force majeure", "witness whereof"
        ],
        "header_patterns": [r"(service|employment|non-disclosure|nda|consulting)\s+agreement", r"contract\s+between"],
        "extractor": "contract_extractor",
        "priority": 2,
    },
    "salary_slip": {
        "label": "Salary Slip",
        "keywords": [
            "employee id", "employee name", "gross salary", "net salary",
            "basic pay", "hra", "pf", "esi", "provident fund",
            "tax deducted", "tds", "allowance", "deduction",
            "pay period", "department", "designation", "ctc"
        ],
        "header_patterns": [r"salary\s+slip", r"pay\s+slip", r"payroll\s+statement"],
        "extractor": "salary_extractor",
        "priority": 1,
    },
    "utility_bill": {
        "label": "Utility Bill",
        "keywords": [
            "electricity", "water", "gas", "internet", "broadband",
            "meter reading", "units consumed", "billing period",
            "service address", "account id", "bill number",
            "previous reading", "current reading", "tariff"
        ],
        "header_patterns": [r"electricity\s+bill", r"water\s+bill", r"utility\s+bill", r"(broadband|internet)\s+bill"],
        "extractor": "utility_extractor",
        "priority": 1,
    },
    "application_form": {
        "label": "Application Form",
        "keywords": [
            "applicant name", "date of birth", "nationality", "passport",
            "address", "contact number", "email", "signature",
            "declaration", "applied for", "reference number",
            "form number", "please fill", "attach documents"
        ],
        "header_patterns": [r"application\s+form", r"application\s+for", r"registration\s+form"],
        "extractor": "generic_extractor",
        "priority": 2,
    },
    "report": {
        "label": "Report",
        "keywords": [
            "executive summary", "introduction", "methodology", "findings",
            "conclusion", "recommendations", "prepared by", "prepared for",
            "table of contents", "appendix", "references", "fiscal year",
            "quarterly", "annual report", "audit"
        ],
        "header_patterns": [r"(annual|quarterly|monthly|audit|financial)\s+report", r"report\s+on"],
        "extractor": "generic_extractor",
        "priority": 3,
    },
}

# ─────────────────────────────────────────────
# 2. EXTRACTION STRATEGIES (ordered by priority)
# ─────────────────────────────────────────────
EXTRACTION_STRATEGIES = {
    "strategy_a": {
        "name": "Direct Text Layer Extraction",
        "description": "For digital PDFs with embedded text",
        "tools": ["PyMuPDF", "pdfplumber"],
        "default": True,
    },
    "strategy_b": {
        "name": "OCR Fallback",
        "description": "For scanned/image-based PDFs",
        "tools": ["Tesseract", "PaddleOCR"],
        "default": False,
    },
    "strategy_c": {
        "name": "Layout Anchoring",
        "description": "Keyword proximity-based extraction",
        "tools": ["custom"],
        "default": False,
    },
    "strategy_d": {
        "name": "Table Detection Logic",
        "description": "For tabular data: transactions, line items",
        "tools": ["pdfplumber", "camelot"],
        "default": False,
    },
}

# ─────────────────────────────────────────────
# 3. VALIDATION RULES PER DOCUMENT TYPE
# ─────────────────────────────────────────────
VALIDATION_RULES = {
    "invoice": {
        "required_fields": ["invoice_number", "invoice_date", "total_amount", "vendor_name"],
        "amount_must_be_positive": True,
        "date_format": ["%d/%m/%Y", "%Y-%m-%d", "%d-%b-%Y"],
        "total_must_match_items": False,   # set True for strict validation
    },
    "bank_statement": {
        "required_fields": ["account_number", "statement_period", "closing_balance"],
        "balance_check": True,
        "date_format": ["%d/%m/%Y", "%Y-%m-%d"],
    },
    "purchase_order": {
        "required_fields": ["po_number", "vendor_name", "order_total", "po_date"],
        "amount_must_be_positive": True,
        "date_format": ["%d/%m/%Y", "%Y-%m-%d"],
    },
    "contract": {
        "required_fields": ["parties", "effective_date", "governing_law"],
        "date_format": ["%d/%m/%Y", "%Y-%m-%d", "%d %B %Y"],
    },
    "salary_slip": {
        "required_fields": ["employee_name", "employee_id", "gross_salary", "net_salary", "pay_period"],
        "net_must_be_less_than_gross": True,
        "date_format": ["%B %Y", "%m/%Y"],
    },
    "utility_bill": {
        "required_fields": ["account_id", "billing_period", "amount_due"],
        "amount_must_be_positive": True,
        "date_format": ["%d/%m/%Y", "%B %Y"],
    },
    "application_form": {
        "required_fields": ["applicant_name"],
        "date_format": ["%d/%m/%Y", "%Y-%m-%d"],
    },
    "report": {
        "required_fields": ["title", "prepared_by"],
        "date_format": ["%d/%m/%Y", "%Y-%m-%d", "%B %Y"],
    },
}

# ─────────────────────────────────────────────
# 4. CONFIDENCE SCORING THRESHOLDS
# ─────────────────────────────────────────────
CONFIDENCE_CONFIG = {
    "high_threshold": 0.80,       # Store as verified, pass directly
    "medium_threshold": 0.50,     # Store with flag: needs_review
    "low_threshold": 0.25,        # Store as unverified, alert user
    # below low_threshold → reject / use generic fallback

    "scoring_weights": {
        "keyword_match": 0.35,
        "required_fields_present": 0.30,
        "field_format_valid": 0.20,
        "text_layer_quality": 0.15,
    },
}

# ─────────────────────────────────────────────
# 5. STORAGE CONFIGURATION
# ─────────────────────────────────────────────
STORAGE_CONFIG = {
    "output_dir": "output/",
    "save_json": True,
    "save_csv": False,
    "include_raw_text": False,  # set True for debugging
    "include_confidence_report": True,
}