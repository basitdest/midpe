#!/usr/bin/env python3
"""
run.py — MIDPE Command-Line Entry Point

Usage:
    python run.py invoice.pdf
    python run.py invoice.pdf --output ./output
    python run.py invoice.pdf --no-save
    python run.py invoice.pdf --pretty
    python run.py --batch ./folder_of_pdfs/
    python run.py --test

Examples:
    python run.py sample_pdfs/invoice.pdf
    python run.py sample_pdfs/bank_statement.pdf --output ./results
    python run.py --batch sample_pdfs/ --output ./results
    python run.py --test
"""

import argparse
import json
import os
import sys
import glob


def _add_project_root():
    """Ensure the project root is on sys.path so 'midpe' package is importable."""
    root = os.path.dirname(os.path.abspath(__file__))
    if root not in sys.path:
        sys.path.insert(0, root)


def _banner():
    print("\n" + "=" * 60)
    print("  MIDPE — Modular Intelligent Document Processing Engine")
    print("  v1.0.0")
    print("=" * 60)


def _print_summary(result: dict, pretty: bool = False):
    """Print a clean summary of the processing result to stdout."""
    if result.get("status") == "failed":
        print(f"\n  ✗ ERROR: {result.get('error')}")
        return

    m   = result["metadata"]
    c   = result["classification"]
    v   = result["validation"]
    conf = result["confidence"]

    action_symbols = {
        "verified":     "✓",
        "needs_review": "⚠",
        "unverified":   "⚡",
        "rejected":     "✗",
    }
    action = result["storage_action"]
    sym = action_symbols.get(action, "?")

    print(f"\n  File           : {m['filename']}")
    print(f"  Document Type  : {c['label']}")
    print(f"  Classifier Conf: {c['classifier_confidence']:.2%}")
    print(f"  Final Score    : {conf['final_score']:.2%}")
    print(f"  Storage Action : {sym} {action.upper()}")
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
    extracted = result.get("extracted_data", {})
    skip_keys = {"_raw_text_length", "line_items", "transactions", "earnings", "deductions",
                 "detected_tables", "key_value_pairs", "possible_entities"}
    for k, v_val in extracted.items():
        if k in skip_keys or not v_val:
            continue
        label = k.replace("_", " ").title()
        if isinstance(v_val, list):
            print(f"    {label:30s}: [{len(v_val)} items]")
        else:
            print(f"    {label:30s}: {str(v_val)[:80]}")

    if result.get("_saved_to"):
        print(f"\n  → JSON saved to: {result['_saved_to']}")

    print()


def process_single(filepath: str, args) -> dict:
    """Process one PDF file and return the result dict."""
    from midpe.pipeline import process_document

    save = not args.no_save
    result = process_document(
        filepath=filepath,
        save_output=save,
        output_dir=args.output if save else None,
    )
    return result


def run_batch(folder: str, args):
    """Process all PDFs in a folder."""
    pdfs = glob.glob(os.path.join(folder, "*.pdf"))
    if not pdfs:
        print(f"\n  No PDF files found in: {folder}")
        return

    print(f"\n  Found {len(pdfs)} PDF(s) in {folder}\n")
    results = []
    for i, pdf in enumerate(pdfs, 1):
        print(f"  [{i}/{len(pdfs)}] Processing: {os.path.basename(pdf)}")
        result = process_single(pdf, args)
        _print_summary(result, args.pretty)
        results.append(result)

    # Summary table
    print("\n" + "=" * 60)
    print("  BATCH SUMMARY")
    print("=" * 60)
    print(f"  {'File':<35} {'Type':<20} {'Action':<15} {'Score'}")
    print("  " + "-" * 58)
    for r in results:
        fname = r["metadata"]["filename"][:33]
        dtype = r["classification"]["label"][:18]
        action = r["storage_action"]
        score = f"{r['confidence']['final_score']:.0%}"
        print(f"  {fname:<35} {dtype:<20} {action:<15} {score}")
    print()


def run_tests():
    """Run built-in synthetic document tests for all 8 document types."""
    from midpe.pipeline import process_document
    from midpe.sample_data import SAMPLES

    print("\n  Running built-in tests on all 8 document types...\n")
    print(f"  {'Type':<22} {'Label':<22} {'Conf':>6} {'Score':>6} {'Action':<15} {'Valid'}")
    print("  " + "-" * 80)

    passed = 0
    for doc_type, sample in SAMPLES.items():
        result = process_document(
            text=sample["text"],
            filename=sample["filename"],
            save_output=False,
        )
        c = result["classification"]
        conf = result["confidence"]
        valid = result["validation"]["is_valid"]
        detected_correctly = c["doc_type"] == doc_type

        status = "✓" if detected_correctly else "✗"
        if detected_correctly:
            passed += 1

        print(
            f"  {status} {doc_type:<20} {c['label']:<22} "
            f"{c['classifier_confidence']:>5.1%} {conf['final_score']:>5.0%}  "
            f"{conf['storage_action']:<15} {'Yes' if valid else 'No'}"
        )

    print(f"\n  Result: {passed}/8 document types classified correctly\n")


# ─────────────────────────────────────────────────────────────
# CLI ARGUMENT PARSER
# ─────────────────────────────────────────────────────────────

def main():
    _add_project_root()
    _banner()

    parser = argparse.ArgumentParser(
        prog="run.py",
        description="MIDPE — Process any business PDF and extract structured JSON",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "file",
        nargs="?",
        help="Path to a PDF file to process\n  e.g. python run.py invoice.pdf",
    )
    parser.add_argument(
        "--output", "-o",
        default="output",
        metavar="DIR",
        help="Directory to save JSON results (default: ./output)",
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Print JSON to stdout only, do not save to disk",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Print full JSON output to stdout in addition to the summary",
    )
    parser.add_argument(
        "--json-only",
        action="store_true",
        help="Print raw JSON to stdout only (no banner, no summary — useful for piping)",
    )
    parser.add_argument(
        "--batch",
        metavar="FOLDER",
        help="Process all PDFs in a folder\n  e.g. python run.py --batch ./sample_pdfs/",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run built-in tests on all 8 synthetic document types",
    )

    args = parser.parse_args()

    # ── Test mode ──────────────────────────────────────────
    if args.test:
        run_tests()
        return

    # ── Batch mode ─────────────────────────────────────────
    if args.batch:
        run_batch(args.batch, args)
        return

    # ── Single file mode ───────────────────────────────────
    if not args.file:
        parser.print_help()
        print("\n  ERROR: Provide a PDF file path or use --batch / --test\n")
        sys.exit(1)

    if not os.path.isfile(args.file):
        print(f"\n  ERROR: File not found: {args.file}\n")
        sys.exit(1)

    result = process_single(args.file, args)

    if args.json_only:
        # Clean machine-readable output for piping
        print(json.dumps(result, indent=2, default=str))
        return

    _print_summary(result, args.pretty)

    if args.pretty:
        print("\n  ── Full JSON Output ──────────────────────────────────")
        print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()