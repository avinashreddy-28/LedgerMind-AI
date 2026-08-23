"""
graph.py — Root-level entry point for LangGraph Multi-Agent Pipeline
===================================================================
"""
import sys
import os

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

# Ensure project root is in sys.path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.graph import run_pipeline, build_pipeline_graph, PipelineState

if __name__ == "__main__":
    print("=" * 65)
    print("  LedgerMind AI — LangGraph End-to-End Pipeline Execution")
    print("=" * 65)

    invoice_file = os.path.join(project_root, "data", "invoice.csv")
    bank_file = os.path.join(project_root, "data", "bank.csv")
    revenue_file = os.path.join(project_root, "data", "revenue.csv")

    state = run_pipeline(invoice_file, bank_file, revenue_file)
    report = state["final_report"]

    print("\n📊 Final Report Summary:")
    print(f"   • Total Invoices   : {report['total_invoices']}")
    print(f"   • Matched Count    : {report['matched_count']}")
    print(f"   • Unmatched Count  : {report['unmatched_count']}")
    print(f"   • Match Percentage : {report['match_percentage']}%")
    print(f"   • Exception Count  : {report['exception_count']}")

    print("\n📈 Projected Revenue (Q3):")
    for f in report["forecast_values"]:
        print(f"   • {f['month']}: ${f['predicted_revenue']:,}")

    print("\n🤖 AI Forecast Commentary:")
    print("-" * 65)
    print(report["forecast_summary"])
    print("=" * 65)
