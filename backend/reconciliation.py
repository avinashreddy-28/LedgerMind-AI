"""
reconciliation.py
=================
Core reconciliation engine for LedgerMind-AI.

Provides two public functions:
    1. load_data       – reads invoice and bank CSV files into DataFrames.
    2. reconcile_transactions – matches invoices to bank transactions by amount
                               and reports matched, unmatched, and a match %.
"""

import pandas as pd


# ---------------------------------------------------------------------------
# 1. DATA LOADING
# ---------------------------------------------------------------------------

def load_data(invoice_path: str, bank_path: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load invoice and bank-statement CSVs into pandas DataFrames.

    Parameters
    ----------
    invoice_path : str
        File path to the invoice CSV.  Expected columns: invoice_id, amount.
    bank_path : str
        File path to the bank-statement CSV.  Expected columns: txn_id, amount.

    Returns
    -------
    tuple[pd.DataFrame, pd.DataFrame]
        (invoice_df, bank_df) — cleaned DataFrames ready for reconciliation.
    """

    # Read the CSV files into DataFrames.
    # pandas automatically infers column dtypes (e.g. int for amount).
    invoice_df = pd.read_csv(invoice_path)
    bank_df = pd.read_csv(bank_path)

    # Strip any accidental whitespace from column names so that downstream
    # lookups like df["amount"] never fail due to hidden spaces.
    invoice_df.columns = invoice_df.columns.str.strip()
    bank_df.columns = bank_df.columns.str.strip()

    # Strip whitespace from string columns (e.g. invoice_id / txn_id) to
    # prevent mismatches caused by leading/trailing spaces in the source data.
    invoice_df = invoice_df.apply(
        lambda col: col.str.strip() if col.dtype == "object" else col
    )
    bank_df = bank_df.apply(
        lambda col: col.str.strip() if col.dtype == "object" else col
    )

    return invoice_df, bank_df


# ---------------------------------------------------------------------------
# 2. RECONCILIATION
# ---------------------------------------------------------------------------

def reconcile_transactions(
    invoice_df: pd.DataFrame,
    bank_df: pd.DataFrame,
) -> dict:
    """
    Match invoices to bank transactions **by amount**.

    Matching strategy
    -----------------
    For every invoice row we look for a bank transaction whose ``amount``
    equals the invoice ``amount``.  Each bank transaction can only be consumed
    once (first-come, first-served) so that duplicate amounts are handled
    correctly — e.g. two invoices of ₹5 000 won't both match the same single
    bank entry of ₹5 000.

    Parameters
    ----------
    invoice_df : pd.DataFrame
        DataFrame with at least an ``amount`` column (and ideally ``invoice_id``).
    bank_df : pd.DataFrame
        DataFrame with at least an ``amount`` column (and ideally ``txn_id``).

    Returns
    -------
    dict
        {
            "matched"           : pd.DataFrame,   # invoices that found a bank match
            "unmatched"         : pd.DataFrame,   # invoices with no matching bank txn
            "match_percentage"  : float,           # 0-100 scale
        }
    """

    # --- Step 1: Build a list of available bank amounts --------------------
    # We convert the bank amounts to a plain Python list so we can pop entries
    # as they are consumed.  This prevents a single bank transaction from being
    # matched to more than one invoice.
    available_bank_amounts: list = bank_df["amount"].tolist()

    # --- Step 2: Walk through each invoice and try to find a match ---------
    # We'll record True/False for every invoice row indicating whether a
    # matching bank amount was found.
    matched_flags: list[bool] = []

    for invoice_amount in invoice_df["amount"]:
        if invoice_amount in available_bank_amounts:
            # A matching bank transaction exists — consume it so it cannot be
            # reused by a later invoice.
            available_bank_amounts.remove(invoice_amount)
            matched_flags.append(True)
        else:
            # No bank transaction with this amount remains — mark unmatched.
            matched_flags.append(False)

    # --- Step 3: Split invoices into matched / unmatched sets ---------------
    # Convert the boolean list into a pandas Series aligned with invoice_df's
    # index so we can use boolean indexing directly.
    match_series = pd.Series(matched_flags, index=invoice_df.index)

    matched_df = invoice_df[match_series].reset_index(drop=True)
    unmatched_df = invoice_df[~match_series].reset_index(drop=True)

    # --- Step 4: Calculate the match percentage ----------------------------
    total_invoices = len(invoice_df)

    # Guard against division-by-zero when the invoice file is empty.
    if total_invoices == 0:
        match_percentage = 0.0
    else:
        match_percentage = (len(matched_df) / total_invoices) * 100

    # --- Step 5: Return the reconciliation results -------------------------
    return {
        "matched": matched_df,
        "unmatched": unmatched_df,
        "match_percentage": round(match_percentage, 2),
    }


# ---------------------------------------------------------------------------
# Quick self-test — run with:  python -m backend.reconciliation
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import os

    # Resolve paths relative to the project root (one level up from backend/).
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    invoice_csv = os.path.join(base_dir, "data", "invoice.csv")
    bank_csv = os.path.join(base_dir, "data", "bank.csv")

    # Load the data files.
    invoices, bank = load_data(invoice_csv, bank_csv)

    print("=== Invoices ===")
    print(invoices)
    print("\n=== Bank Transactions ===")
    print(bank)

    # Run reconciliation.
    results = reconcile_transactions(invoices, bank)

    print("\n=== Matched Invoices ===")
    print(results["matched"])
    print("\n=== Unmatched Invoices ===")
    print(results["unmatched"])
    print(f"\nMatch Percentage: {results['match_percentage']}%")
