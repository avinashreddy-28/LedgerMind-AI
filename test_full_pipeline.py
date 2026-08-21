"""
test_full_pipeline.py
======================
End-to-end test: load data → reconcile → generate AI exceptions.
"""

import os
import sys

# Project root on path.
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Fix encoding for Windows console.
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

from backend.reconciliation import load_data, reconcile_transactions, generate_exceptions

# Step 1: Load CSVs.
invoice_df, bank_df = load_data("data/invoice.csv", "data/bank.csv")
print(f"Loaded {len(invoice_df)} invoices, {len(bank_df)} bank transactions.\n")

# Step 2: Reconcile.
results = reconcile_transactions(invoice_df, bank_df)
print(f"Matched   : {len(results['matched'])}")
print(f"Unmatched : {len(results['unmatched'])}")
print(f"Match %   : {results['match_percentage']}%\n")

# Step 3: Generate AI exceptions for unmatched invoices.
unmatched = results["unmatched"]
print("=" * 60)
print("  AI EXCEPTION REPORT")
print("=" * 60)

exceptions_df = generate_exceptions(unmatched)

for _, row in exceptions_df.iterrows():
    print(f"\n📌 Invoice: {row['invoice_id']}  |  Amount: {row['amount']:,.2f}")
    print("-" * 60)
    print(row["explanation"])
    print("-" * 60)
