"""
test_reconciliation.py
======================
Quick integration test for the reconciliation module.

Loads the sample invoice and bank CSVs, runs reconciliation,
and prints a summary report to the console.
"""

import os
import sys

# Ensure the project root is on the Python path so that
# "from backend.reconciliation import ..." works regardless
# of where the script is invoked from.
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from backend.reconciliation import load_data, reconcile_transactions


def main():
    # --- 1. Resolve file paths relative to the project root ----------------
    invoice_path = os.path.join(project_root, "data", "invoice.csv")
    bank_path = os.path.join(project_root, "data", "bank.csv")

    # --- 2. Load the data using the reconciliation module ------------------
    invoice_df, bank_df = load_data(invoice_path, bank_path)

    # --- 3. Run reconciliation ---------------------------------------------
    results = reconcile_transactions(invoice_df, bank_df)

    # --- 4. Print the summary report ---------------------------------------
    print("=" * 50)
    print("       RECONCILIATION TEST REPORT")
    print("=" * 50)

    print(f"\nTotal Invoices     : {len(invoice_df)}")
    print(f"Matched Invoices   : {len(results['matched'])}")
    print(f"Unmatched Invoices : {len(results['unmatched'])}")
    print(f"Match Percentage   : {results['match_percentage']}%")

    # Show the matched and unmatched details for quick inspection.
    print("\n--- Matched Invoices ---")
    print(results["matched"].to_string(index=False))

    print("\n--- Unmatched Invoices ---")
    print(results["unmatched"].to_string(index=False))

    print("\n" + "=" * 50)


if __name__ == "__main__":
    main()
