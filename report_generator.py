"""
report_generator.py — Root-level entry point for PDF Report Generator
=====================================================================
"""
import os
import sys

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

# Ensure project root is in sys.path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.report_generator import generate_pdf_report
from backend.graph import run_pipeline

if __name__ == "__main__":
    print("=" * 65)
    print("  LedgerMind AI — Running Full Pipeline & Generating PDF Report")
    print("=" * 65)

    invoice_file = os.path.join(project_root, "data", "invoice.csv")
    bank_file = os.path.join(project_root, "data", "bank.csv")
    revenue_file = os.path.join(project_root, "data", "revenue.csv")

    state = run_pipeline(invoice_file, bank_file, revenue_file)
    pdf_path = generate_pdf_report(state, output_path=os.path.join(project_root, "reports", "ledgermind_report.pdf"))

    print(f"\n✅ PDF Report successfully generated at:\n   {pdf_path}")
    print(f"   File size: {os.path.getsize(pdf_path):,} bytes")
    print("=" * 65)
