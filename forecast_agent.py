"""
forecast_agent.py — Root-level entry point for Forecast Agent
=============================================================
"""
import sys
import os

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

# Ensure project root is in sys.path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import pandas as pd
from backend.forecast_agent import forecast_revenue, explain_forecast

if __name__ == "__main__":
    revenue_csv = os.path.join(project_root, "data", "revenue.csv")
    print("=" * 60)
    print("  LedgerMind AI — Forecast Agent Standalone Test")
    print("=" * 60)

    # 1. Forecast revenue
    hist_df = pd.read_csv(revenue_csv)
    pred_df = forecast_revenue(revenue_csv, months_ahead=3)
    
    print("\n📈 Historical Revenue:")
    for _, r in hist_df.iterrows():
        print(f"   {r['month']}: ${r['revenue']:,}")

    print("\n🔮 Predicted Revenue (Next 3 Months):")
    for _, r in pred_df.iterrows():
        print(f"   {r['month']}: ${r['predicted_revenue']:,}")

    # 2. Generate AI Commentary
    print("\n🤖 AI Forecast Commentary:")
    print("-" * 60)
    summary = explain_forecast(hist_df, pred_df)
    print(summary)
    print("=" * 60)
