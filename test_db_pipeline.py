"""
test_db_pipeline.py
===================
Full end-to-end test:
  1. init_db()            — create the invoices table
  2. load + reconcile     — match invoices to bank transactions
  3. generate_exceptions  — AI explanations for unmatched invoices
  4. save_to_db()         — persist all results to the database
  5. Query + print rows   — verify data was written correctly
"""

import sys
import os

# Ensure UTF-8 output on Windows consoles.
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

# Ensure project root is on sys.path.
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import pandas as pd
from backend.db import init_db, get_engine, _active_backend
from backend.reconciliation import (
    load_data,
    reconcile_transactions,
    generate_exceptions,
    save_to_db,
)

print("=" * 60)
print("  LedgerMind-AI — DB Pipeline Test")
print("=" * 60)

# ---------------------------------------------------------------------------
# Step 1: Initialise the database / create table
# ---------------------------------------------------------------------------
print("\n📦 Step 1: Initialising database...")
init_db()
print(f"   Active backend: {_active_backend}")

# ---------------------------------------------------------------------------
# Step 2: Load CSVs and run reconciliation
# ---------------------------------------------------------------------------
print("\n📂 Step 2: Loading CSVs and reconciling...")
invoice_csv = os.path.join(project_root, "data", "invoice.csv")
bank_csv    = os.path.join(project_root, "data", "bank.csv")

invoices, bank = load_data(invoice_csv, bank_csv)
results = reconcile_transactions(invoices, bank)

matched_df   = results["matched"]
unmatched_df = results["unmatched"]
print(f"   ✅ Matched  : {len(matched_df)}")
print(f"   ❌ Unmatched: {len(unmatched_df)}")
print(f"   📊 Match %  : {results['match_percentage']}%")

# ---------------------------------------------------------------------------
# Step 3: Generate AI exceptions for unmatched invoices
# ---------------------------------------------------------------------------
if unmatched_df.empty:
    print("\n🎉 All invoices matched — skipping AI exception generation.")
    exceptions_df = pd.DataFrame(columns=["invoice_id", "amount", "explanation"])
else:
    print(f"\n🤖 Step 3: Generating AI explanations for {len(unmatched_df)} invoice(s)...")
    print("   (3-second delay between calls to respect rate limits)")
    exceptions_df = generate_exceptions(unmatched_df)
    print("   Done.")

# ---------------------------------------------------------------------------
# Step 4: Save all results to the database
# ---------------------------------------------------------------------------
print("\n💾 Step 4: Saving to database...")
save_to_db(matched_df, exceptions_df)

# ---------------------------------------------------------------------------
# Step 5: Query the invoices table and print all rows
# ---------------------------------------------------------------------------
print("\n📋 Step 5: Querying 'invoices' table...")
engine = get_engine()
df = pd.read_sql("SELECT * FROM invoices ORDER BY status, invoice_id", engine)

print(f"\n{'=' * 60}")
print(f"  INVOICES TABLE — {len(df)} rows")
print(f"{'=' * 60}")

for _, row in df.iterrows():
    status_icon = "✅" if row["status"] == "MATCHED" else "❌"
    print(f"\n{status_icon}  {row['invoice_id']}  |  ${float(row['amount']):,.2f}  |  {row['status']}")
    if row["explanation"] and str(row["explanation"]).strip() not in ("", "nan", "None"):
        print("   Explanation:")
        for line in str(row["explanation"]).strip().split("\n"):
            print(f"     {line}")

print(f"\n{'=' * 60}")
print(f"✅ Pipeline complete — {len(df)} invoice(s) stored in '{_active_backend}'.")
