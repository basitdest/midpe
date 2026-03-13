"""
tests/generate_sample_pdfs.py
Generates real PDF files for all 8 document types using reportlab.
Run this once to populate sample_pdfs/ with test files.

Usage:
    python tests/generate_sample_pdfs.py
"""

import os
import sys

# Ensure project root on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT
except ImportError:
    print("ERROR: reportlab not installed. Run: pip install reportlab")
    sys.exit(1)

from midpe.sample_data import SAMPLES

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sample_pdfs")


def make_pdf(text: str, out_path: str, title: str = "Document"):
    """Convert a plain text string into a formatted PDF."""
    doc = SimpleDocTemplate(
        out_path,
        pagesize=A4,
        leftMargin=20*mm,
        rightMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleStyle", parent=styles["Heading1"],
        fontSize=14, spaceAfter=6, alignment=TA_CENTER,
    )
    normal_style = ParagraphStyle(
        "NormalStyle", parent=styles["Normal"],
        fontSize=9, leading=14, spaceAfter=2,
    )
    mono_style = ParagraphStyle(
        "MonoStyle", parent=styles["Normal"],
        fontSize=8, leading=13, fontName="Courier", spaceAfter=1,
    )

    story = []

    lines = text.strip().split("\n")
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            story.append(Spacer(1, 4))
            continue
        # First non-empty line as title
        if i == 0 or (i <= 3 and line.isupper()):
            story.append(Paragraph(line, title_style))
        else:
            # Use monospace for lines with numbers/colons (structured data)
            if ":" in line or any(c.isdigit() for c in line):
                story.append(Paragraph(line.replace("$", "&#36;").replace("&", "&amp;"), mono_style))
            else:
                story.append(Paragraph(line, normal_style))

    doc.build(story)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"\nGenerating sample PDFs → {OUTPUT_DIR}/\n")

    for doc_type, sample in SAMPLES.items():
        out_path = os.path.join(OUTPUT_DIR, sample["filename"])
        try:
            make_pdf(sample["text"], out_path, title=sample["filename"])
            size = os.path.getsize(out_path) // 1024
            print(f"  ✓ {sample['filename']:<55} {size}KB")
        except Exception as e:
            print(f"  ✗ {sample['filename']}: {e}")

    print(f"\nDone. Run the pipeline on any file:")
    print(f"  python run.py sample_pdfs/Nexus_Tech_Invoice_INV-2024-00847.pdf\n")


if __name__ == "__main__":
    main()