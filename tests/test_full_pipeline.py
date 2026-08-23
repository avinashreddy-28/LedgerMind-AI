"""
test_full_pipeline.py — Verification of LangGraph End-to-End Pipeline
=====================================================================
"""
import os
import sys

# Ensure UTF-8 console output on Windows
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

# Ensure project root is in sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.graph import run_pipeline

if __name__ == "__main__":
    print("=" * 65)
    print("  LedgerMind AI — Testing Full LangGraph Pipeline")
    print("=" * 65)

    invoice_path = "data/invoice.csv"
    bank_path = "data/bank.csv"
    revenue_path = "data/revenue.csv"

    # Execute full pipeline
    final_state = run_pipeline(invoice_path, bank_path, revenue_path)
    final_report = final_state["final_report"]

    print("\n📦 Final Report Returned from State:")
    print("-" * 65)
    for k, v in final_report.items():
        if k == "forecast_values":
            print(f"  {k}:")
            for item in v:
                print(f"    - {item['month']}: ${item['predicted_revenue']:,}")
        elif k == "forecast_summary":
            print(f"\n  {k}:\n    {v}")
        else:
            print(f"  {k}: {v}")

    print("\n" + "=" * 65)
    print("  LangGraph Pipeline Execution Verified Successfully!")
    print("=" * 65)
