"""
reconciliation.py
=================
Core reconciliation engine for LedgerMind-AI.

Provides four public functions:
    1. load_data              – reads invoice and bank CSV files into DataFrames.
    2. reconcile_transactions – matches invoices to bank transactions by amount
                                and reports matched, unmatched, and a match %.
    3. generate_exceptions    – uses AI to explain each unmatched invoice.
    4. save_to_db             – persists reconciliation results to PostgreSQL.
"""

import time

import pandas as pd


# ---------------------------------------------------------------------------
# 1. DATA LOADING
# ---------------------------------------------------------------------------

def load_data(invoice_path: str, bank_path: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load invoice and bank-statement CSVs into pandas DataFrames with robust error handling.

    Parameters
    ----------
    invoice_path : str
        File path to the invoice CSV. Expected columns: invoice_id, amount.
    bank_path : str
        File path to the bank-statement CSV. Expected columns: txn_id, amount.

    Returns
    -------
    tuple[pd.DataFrame, pd.DataFrame]
        (invoice_df, bank_df) — cleaned DataFrames ready for reconciliation.
    """
    import os

    # Check file existence if paths are strings or PathLike
    if isinstance(invoice_path, (str, os.PathLike)):
        if not os.path.exists(invoice_path):
            raise FileNotFoundError(f"Invoice CSV file not found at: {invoice_path}")
    if isinstance(bank_path, (str, os.PathLike)):
        if not os.path.exists(bank_path):
            raise FileNotFoundError(f"Bank statement CSV file not found at: {bank_path}")

    # Read the CSV files into DataFrames (supports filepath, UploadedFile, or BytesIO)
    try:
        if hasattr(invoice_path, "seek"):
            invoice_path.seek(0)
        invoice_df = pd.read_csv(invoice_path)
    except Exception as e:
        raise ValueError(f"Could not parse invoice CSV: {e}")

    try:
        if hasattr(bank_path, "seek"):
            bank_path.seek(0)
        bank_df = pd.read_csv(bank_path)
    except Exception as e:
        raise ValueError(f"Could not parse bank CSV: {e}")

    # Validate required columns
    if "amount" not in invoice_df.columns:
        raise ValueError(f"Invoice CSV missing required 'amount' column. Found: {list(invoice_df.columns)}")
    if "amount" not in bank_df.columns:
        raise ValueError(f"Bank CSV missing required 'amount' column. Found: {list(bank_df.columns)}")

    # Strip any accidental whitespace from column names
    invoice_df.columns = invoice_df.columns.str.strip()
    bank_df.columns = bank_df.columns.str.strip()

    # Strip whitespace from string columns
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
# 3. AI-POWERED EXCEPTION ANALYSIS
# ---------------------------------------------------------------------------

def generate_exceptions(unmatched_df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate AI-powered explanations for every unmatched invoice.

    For each row in *unmatched_df*, the Gemini-backed
    :func:`backend.exception_agent.explain_exception` is called to produce
    a human-readable explanation of why the invoice might not have a
    matching bank transaction.

    A 1-second delay is inserted between API calls to stay within
    free-tier rate limits.

    Parameters
    ----------
    unmatched_df : pd.DataFrame
        DataFrame of invoices that had no bank match.
        Must contain ``invoice_id`` and ``amount`` columns.

    Returns
    -------
    pd.DataFrame
        A new DataFrame with columns:
        ``invoice_id``, ``amount``, ``explanation``.
    """

    # Import the AI agent here (lazy import) so the rest of the module
    # stays usable even when the Gemini key isn't configured.
    from backend.exception_agent import explain_exception

    # --- Step 1: Prepare a list to collect results -------------------------
    exception_records: list[dict] = []

    # --- Step 2: Iterate over each unmatched invoice -----------------------
    total = len(unmatched_df)
    for idx, row in unmatched_df.iterrows():
        invoice_id = row["invoice_id"]
        amount = row["amount"]

        # Call the AI agent to generate a plain-text explanation.
        explanation = explain_exception(invoice_id, amount)

        # Store the result.
        exception_records.append({
            "invoice_id": invoice_id,
            "amount": amount,
            "explanation": explanation,
        })
        # --- Step 3: Rate-limit guard -------------------------------------
        # Pause 3 seconds between calls to avoid hitting API rate limits.
        # Skip the delay after the last item to keep things snappy.
        if idx < total - 1:
            time.sleep(3)

    # --- Step 4: Build and return the results DataFrame --------------------
    exceptions_df = pd.DataFrame(exception_records)
    return exceptions_df


# ---------------------------------------------------------------------------
# 4. PERSIST RESULTS TO DATABASE
# ---------------------------------------------------------------------------

def save_to_db(
    matched_df: pd.DataFrame,
    unmatched_with_exceptions_df: pd.DataFrame,
) -> None:
    """
    Persist reconciliation results to the PostgreSQL "invoices" table.

    This function merges matched and unmatched DataFrames into a single
    table with a ``status`` column and writes it to the database, replacing
    any previous data in the table.

    Parameters
    ----------
    matched_df : pd.DataFrame
        Invoices that were successfully matched to bank transactions.
        Must contain ``invoice_id`` and ``amount`` columns.
    unmatched_with_exceptions_df : pd.DataFrame
        Unmatched invoices enriched with AI explanations.
        Must contain ``invoice_id``, ``amount``, and ``explanation`` columns.

    Raises
    ------
    sqlalchemy.exc.OperationalError
        If the database is unreachable.
    """

    # --- Step 1: Prepare the matched rows ---------------------------------
    # Copy to avoid mutating the caller's DataFrame.
    matched = matched_df[["invoice_id", "amount"]].copy()

    # Tag every matched invoice with status="MATCHED" and no explanation.
    matched["status"] = "MATCHED"
    matched["explanation"] = None

    # --- Step 2: Prepare the unmatched rows --------------------------------
    # These already carry an "explanation" column from generate_exceptions().
    unmatched = unmatched_with_exceptions_df[
        ["invoice_id", "amount", "explanation"]
    ].copy()

    # Tag every unmatched invoice.
    unmatched["status"] = "UNMATCHED"

    # --- Step 3: Combine into one DataFrame --------------------------------
    # Column order: invoice_id | amount | status | explanation
    combined = pd.concat([matched, unmatched], ignore_index=True)
    combined = combined[["invoice_id", "amount", "status", "explanation"]]

    # --- Step 4: Write to the database -------------------------------------
    # Lazy-import db.py so that reconciliation.py stays usable even when
    # PostgreSQL is not configured (e.g. during CSV-only testing).
    from backend.db import get_engine

    engine = get_engine()

    # to_sql writes the DataFrame to the "invoices" table.
    # if_exists="replace" drops and recreates the table each time so we
    # always reflect the latest reconciliation run.
    # index=False prevents pandas from writing the DataFrame index as a column.
    combined.to_sql(
        name="invoices",
        con=engine,
        if_exists="replace",
        index=False,
    )

    print(
        f"✅ Saved {len(combined)} rows to 'invoices' table "
        f"({len(matched)} matched, {len(unmatched)} unmatched)."
    )


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
