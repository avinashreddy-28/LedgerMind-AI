"""
run_pipeline.py
===============
End-to-end pipeline:
    1. Load invoice.csv and bank.csv
    2. Reconcile transactions
    3. Generate AI explanations for unmatched invoices
    4. Print invoice_id, amount, and explanation for each
"""

import os
import sys

# Ensure UTF-8 output on Windows consoles.
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------------------
# Step 1: Load the data
# ---------------------------------------------------------------------------
from backend.reconciliation import load_data, reconcile_transactions, generate_exceptions

base_dir = os.path.dirname(os.path.abspath(__file__))
invoice_csv = os.path.join(base_dir, "data", "invoice.csv")
bank_csv = os.path.join(base_dir, "data", "bank.csv")

print("=" * 60)
print("  LedgerMind-AI  —  Full Pipeline Run")
print("=" * 60)

print("\n📂 Loading data...")
invoices, bank = load_data(invoice_csv, bank_csv)
print(f"   Invoices loaded : {len(invoices)} rows")
print(f"   Bank txns loaded: {len(bank)} rows")

# ---------------------------------------------------------------------------
# Step 2: Reconcile
# ---------------------------------------------------------------------------
print("\n🔍 Running reconciliation...")
results = reconcile_transactions(invoices, bank)

matched = results["matched"]
unmatched = results["unmatched"]
pct = results["match_percentage"]

print(f"   ✅ Matched   : {len(matched)}")
print(f"   ❌ Unmatched : {len(unmatched)}")
print(f"   📊 Match %   : {pct}%")

# ---------------------------------------------------------------------------
# Step 3: Generate AI explanations for unmatched invoices
# ---------------------------------------------------------------------------
if unmatched.empty:
    print("\n🎉 All invoices matched — no exceptions to analyse!")
else:
    print(f"\n🤖 Generating AI explanations for {len(unmatched)} unmatched invoice(s)...")
    print("   (This may take a few seconds due to API rate-limiting)\n")

    exceptions_df = generate_exceptions(unmatched)

    # -----------------------------------------------------------------------
    # Step 4: Print results
    # -----------------------------------------------------------------------
    print("=" * 60)
    print("  EXCEPTION REPORT")
    print("=" * 60)

    for _, row in exceptions_df.iterrows():
        print(f"\n{'─' * 60}")
        print(f"  Invoice ID : {row['invoice_id']}")
        print(f"  Amount     : {row['amount']:,.2f}")
        print(f"  Explanation:")
        # Indent the explanation lines for readability.
        for line in row["explanation"].strip().split("\n"):
            print(f"    {line}")

    print(f"\n{'─' * 60}")
    print(f"\n✅ Pipeline complete — {len(exceptions_df)} exception(s) analysed.")
