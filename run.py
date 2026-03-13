#!/usr/bin/env python3
"""
run.py — MIDPE Command-Line Entry Point

Usage:
    python run.py invoice.pdf
    python run.py invoice.pdf --output ./results
    python run.py invoice.pdf --no-save
    python run.py invoice.pdf --pretty
    python run.py invoice.pdf --json-only
    python run.py --batch ./sample_pdfs/
    python run.py --test
"""

import os
import sys

# ── Always resolve imports relative to this file's directory ──
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


# ─────────────────────────────────────────────────────────────
# STARTUP CHECK
# ─────────────────────────────────────────────────────────────

def check_structure():
    """Verify all required files exist before importing anything."""
    required = [
        "midpe/__init__.py",
        "midpe/config.py",
        "midpe/pipeline.py",
        "midpe/sample_data.py",
        "midpe/classification/__init__.py",
        "midpe/classification/classifier.py",
        "midpe/extraction/__init__.py",
        "midpe/extraction/base_extractor.py",
        "midpe/extraction/strategy_selector.py",
        "midpe/extraction/invoice_extractor.py",
        "midpe/extraction/bank_extractor.py",
        "midpe/extraction/po_extractor.py",
        "midpe/extraction/contract_extractor.py",
        "midpe/extraction/salary_extractor.py",
        "midpe/extraction/utility_extractor.py",
        "midpe/extraction/generic_extractor.py",
        "midpe/validation/__init__.py",
        "midpe/validation/validator.py",
        "midpe/confidence/__init__.py",
        "midpe/confidence/scorer.py",
    ]
    missing = [p for p in required if not os.path.isfile(os.path.join(ROOT, p))]
    if missing:
        print("\n  ERROR: Missing files:")
        for f in missing:
            print(f"    MISSING → {f}")
        print("\n  Re-download the full MIDPE project to restore them.\n")
        sys.exit(1)


def check_imports():
    """
    Fix incorrect bare imports in midpe modules.
    IMPORTANT: base_extractor.py is excluded — it has no internal imports
    and patching it would cause a circular import.
    """
    import re

    # base_extractor.py is deliberately excluded from this list
    targets = [
        "midpe/classification/classifier.py",
        "midpe/validation/validator.py",
        "midpe/confidence/scorer.py",
        "midpe/extraction/strategy_selector.py",
        "midpe/extraction/invoice_extractor.py",
        "midpe/extraction/bank_extractor.py",
        "midpe/extraction/po_extractor.py",
        "midpe/extraction/contract_extractor.py",
        "midpe/extraction/salary_extractor.py",
        "midpe/extraction/utility_extractor.py",
        "midpe/extraction/generic_extractor.py",
        "midpe/pipeline.py",
    ]

    fixes = [
        (r"^from config import",    "from midpe.config import"),
        (r"^from extraction\.",     "from midpe.extraction."),
        (r"^from classification\.", "from midpe.classification."),
        (r"^from validation\.",     "from midpe.validation."),
        (r"^from confidence\.",     "from midpe.confidence."),
    ]

    fixed_files = []
    for rel in targets:
        fpath = os.path.join(ROOT, rel)
        if not os.path.isfile(fpath):
            continue
        with open(fpath, "r", encoding="utf-8") as f:
            original = f.read()
        patched = original
        for pattern, replacement in fixes:
            patched = re.sub(pattern, replacement, patched, flags=re.MULTILINE)
        if patched != original:
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(patched)
            fixed_files.append(rel)

    if fixed_files:
        print("  [auto-fixed] Import paths corrected in:")
        for f in fixed_files:
            print(f"    {f}")


def check_base_extractor():
    """
    Detect and fix circular import in base_extractor.py.
    This happens when the auto-fix script accidentally adds a self-import.
    """
    fpath = os.path.join(ROOT, "midpe", "extraction", "base_extractor.py")
    if not os.path.isfile(fpath):
        return
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()
    # If base_extractor imports from itself — remove those lines
    if "from midpe.extraction.base_extractor import" in content:
        lines = content.splitlines()
        cleaned = [l for l in lines if "from midpe.extraction.base_extractor import" not in l]
        with open(fpath, "w", encoding="utf-8") as f:
            f.write("\n".join(cleaned))
        print("  [auto-fixed] Removed circular self-import from base_extractor.py")


# Run all checks on startup
check_structure()
check_base_extractor()   # must run before check_imports
check_imports()


# ─────────────────────────────────────────────────────────────
# Safe to import now
# ─────────────────────────────────────────────────────────────

import argparse
import json
import glob


def _banner():
    print("\n" + "=" * 60)
    print("  MIDPE — Modular Intelligent Document Processing Engine")
    print("  v1.0.0")
    print("=" * 60)


def _print_summary(result: dict):
    if result.get("status") == "failed":
        print(f"\n  ERROR: {result.get('error')}\n")
        return

    m    = result["metadata"]
    c    = result["classification"]
    v    = result["validation"]
    conf = result["confidence"]

    symbols = {"verified": "✓", "needs_review": "⚠", "unverified": "⚡", "rejected": "✗"}
    action = result["storage_action"]

    print(f"\n  File           : {m['filename']}")
    print(f"  Document Type  : {c['label']}")
    print(f"  Classifier Conf: {c['classifier_confidence']:.2%}")
    print(f"  Final Score    : {conf['final_score']:.2%}")
    print(f"  Storage Action : {symbols.get(action, '?')} {action.upper()}")
    print(f"  Valid          : {'Yes' if v['is_valid'] else 'No'}")
    print(f"  Processing     : {m['processing_time_ms']}ms")

    if v["errors"]:
        print(f"\n  Validation Errors:")
        for e in v["errors"]:
            print(f"    - {e}")

    if v["warnings"]:
        print(f"\n  Warnings:")
        for w in v["warnings"]:
            print(f"    ~ {w}")

    print(f"\n  Extracted Fields:")
    skip = {
        "_raw_text_length", "line_items", "transactions", "earnings",
        "deductions", "detected_tables", "key_value_pairs", "possible_entities",
    }
    for k, val in result.get("extracted_data", {}).items():
        if k in skip or not val:
            continue
        label   = k.replace("_", " ").title()
        display = f"[{len(val)} items]" if isinstance(val, list) else str(val)[:80]
        print(f"    {label:30s}: {display}")

    if result.get("_saved_to"):
        print(f"\n  JSON saved to  : {result['_saved_to']}")
    print()


def _process_single(filepath: str, args) -> dict:
    from midpe.pipeline import process_document
    return process_document(
        filepath=filepath,
        save_output=not args.no_save,
        output_dir=args.output if not args.no_save else None,
    )


def _run_batch(folder: str, args):
    pdfs = glob.glob(os.path.join(folder, "*.pdf"))
    if not pdfs:
        print(f"\n  No PDF files found in: {folder}\n")
        return

    print(f"\n  Found {len(pdfs)} PDF(s) in: {folder}\n")
    results = []
    for i, pdf in enumerate(pdfs, 1):
        print(f"  [{i}/{len(pdfs)}] {os.path.basename(pdf)}")
        r = _process_single(pdf, args)
        _print_summary(r)
        results.append(r)

    print("=" * 60)
    print("  BATCH SUMMARY")
    print("=" * 60)
    print(f"  {'File':<35} {'Type':<20} {'Action':<15} {'Score'}")
    print("  " + "-" * 58)
    for r in results:
        print(
            f"  {r['metadata']['filename'][:33]:<35}"
            f" {r['classification']['label'][:18]:<20}"
            f" {r['storage_action']:<15}"
            f" {r['confidence']['final_score']:.0%}"
        )
    print()


def _run_tests():
    from midpe.pipeline import process_document
    from midpe.sample_data import SAMPLES

    print("\n  Running built-in tests on all 8 document types...\n")
    print(f"  {'':2} {'Type':<22} {'Detected As':<22} {'Conf':>6} {'Score':>6}  {'Action':<15} {'Valid'}")
    print("  " + "─" * 80)

    passed = 0
    for doc_type, sample in SAMPLES.items():
        r    = process_document(text=sample["text"], filename=sample["filename"], save_output=False)
        c    = r["classification"]
        conf = r["confidence"]
        ok   = c["doc_type"] == doc_type
        if ok:
            passed += 1
        print(
            f"  {'✓' if ok else '✗'}  {doc_type:<22} {c['label']:<22}"
            f" {c['classifier_confidence']:>5.1%} {conf['final_score']:>5.0%}"
            f"  {conf['storage_action']:<15} {'Yes' if r['validation']['is_valid'] else 'No'}"
        )

    print(f"\n  Result: {passed}/8 document types classified correctly\n")


# ─────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────

def main():
    _banner()

    parser = argparse.ArgumentParser(
        prog="run.py",
        description="MIDPE — Process any business PDF and return structured JSON",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("--output", "-o", default="output", metavar="DIR",
                        help="Folder to save JSON results (default: ./output)")
    parser.add_argument("--no-save", action="store_true",
                        help="Print summary only — do not write JSON to disk")
    parser.add_argument("--pretty", action="store_true",
                        help="Also print the full JSON to the terminal")
    parser.add_argument("--json-only", action="store_true",
                        help="Print raw JSON only (good for piping)")
    parser.add_argument("--batch", metavar="FOLDER",
                        help="Process every PDF in a folder\n  e.g. python run.py --batch sample_pdfs/")
    parser.add_argument("--test", action="store_true",
                        help="Run built-in tests on all 8 document types (no PDF needed)")

    args, leftovers = parser.parse_known_args()

    if args.test:
        _run_tests()
        return

    if args.batch:
        _run_batch(args.batch, args)
        return

    filepath = leftovers[0] if leftovers else None

    if not filepath:
        parser.print_help()
        print("\n  Examples:")
        print("    python run.py invoice.pdf")
        print("    python run.py invoice.pdf --json-only")
        print("    python run.py --batch sample_pdfs/")
        print("    python run.py --test\n")
        sys.exit(0)

    if filepath.startswith("-") and not os.path.isfile(filepath):
        print(f"\n  ERROR: '{filepath}' looks like a flag, not a filename.")
        print(f"  Did you mean:  python run.py {filepath.lstrip('-')}\n")
        sys.exit(1)

    if not os.path.isfile(filepath):
        print(f"\n  ERROR: File not found: {filepath}")
        print(f"  Example:  python run.py sample_pdfs\\Nexus_Tech_Invoice_INV-2024-00847.pdf\n")
        sys.exit(1)

    args.file = filepath
    result = _process_single(filepath, args)

    if args.json_only:
        print(json.dumps(result, indent=2, default=str))
        return

    _print_summary(result)

    if args.pretty:
        print("  ── Full JSON ─────────────────────────────────────────")
        print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
