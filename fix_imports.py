"""
fix_imports.py
Run this once if you see 'ModuleNotFoundError: No module named config'.
It patches all import statements across the midpe package to use
the correct 'midpe.X' prefix.

Usage:
    python fix_imports.py
"""
import os
import re

ROOT = os.path.join(os.path.dirname(__file__), "midpe")

REPLACEMENTS = [
    # bare config import → midpe.config
    (r"^from config import",          "from midpe.config import"),
    (r"^import config$",              "import midpe.config as config"),
    # bare extraction.X imports → midpe.extraction.X
    (r"^from extraction\.",           "from midpe.extraction."),
    (r"^from classification\.",       "from midpe.classification."),
    (r"^from validation\.",           "from midpe.validation."),
    (r"^from confidence\.",           "from midpe.confidence."),
]

fixed_files = []

for dirpath, _, filenames in os.walk(ROOT):
    for fname in filenames:
        if not fname.endswith(".py"):
            continue
        fpath = os.path.join(dirpath, fname)
        with open(fpath, "r", encoding="utf-8") as f:
            original = f.read()

        patched = original
        for pattern, replacement in REPLACEMENTS:
            patched = re.sub(pattern, replacement, patched, flags=re.MULTILINE)

        if patched != original:
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(patched)
            rel = os.path.relpath(fpath, os.path.dirname(ROOT))
            fixed_files.append(rel)

if fixed_files:
    print("Fixed imports in:")
    for f in fixed_files:
        print(f"  {f}")
else:
    print("All imports already correct — nothing to fix.")

print("\nDone. Try running again:")
print("  python run.py --test")
