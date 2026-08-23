"""
copilot_agent.py — LedgerMind AI Copilot
==========================================
Natural-language interface to the LedgerMind database.

The copilot turns a plain English question into a SQL query, executes it
against the invoices table, then converts the raw results back into a
human-readable answer — all powered by Gemini.

Two-pass Gemini architecture:
    Pass 1: Question  → SQL query
    Pass 2: SQL data  → Human-readable answer

Public API:
    ask_copilot(user_question: str) -> str

Usage:
    from backend.copilot_agent import ask_copilot
    answer = ask_copilot("How many invoices are unmatched?")
    print(answer)
"""

import os
import re
import sys

# ---------------------------------------------------------------------------
# 1. Load environment variables from .env
# ---------------------------------------------------------------------------
from dotenv import load_dotenv

# Resolve the project root (one level up from backend/).
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(project_root, ".env")
load_dotenv(dotenv_path)

# ---------------------------------------------------------------------------
# 2. Configure the Gemini client
# ---------------------------------------------------------------------------
from google import genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Build a reusable client.  If the key is missing every call returns a
# graceful fallback string rather than raising an exception.
_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

# Candidate models in order of preference
CANDIDATE_MODELS = ["gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.5-flash-lite"]


def _generate_content_with_fallback(contents: str) -> str:
    """
    Attempts generation with the primary model, falling back to alternatives
    if quota or rate limits are encountered.
    """
    last_err = None
    for model in CANDIDATE_MODELS:
        try:
            res = _client.models.generate_content(
                model=model,
                contents=contents,
            )
            return res.text.strip()
        except Exception as e:
            last_err = e
            continue
    raise last_err

# ---------------------------------------------------------------------------
# 3. Table schema — injected into the SQL-generation prompt
# ---------------------------------------------------------------------------
# Keep this in sync with backend/db.py if the schema ever changes.
TABLE_SCHEMA = """
Table: invoices
Columns:
  - invoice_id  VARCHAR(50)  PRIMARY KEY   -- e.g. "INV001"
  - amount      NUMERIC(15,2) NOT NULL      -- invoice amount in dollars
  - status      VARCHAR(20)  NOT NULL       -- "MATCHED" or "UNMATCHED"
  - explanation TEXT         NULLABLE       -- AI-generated reason for mismatch (NULL for matched rows)
"""

# ---------------------------------------------------------------------------
# 4. Safety check — block any non-SELECT statement
# ---------------------------------------------------------------------------
# These keywords indicate destructive or mutating SQL that we never want to
# run from a natural-language interface.
_BLOCKED_KEYWORDS = ("insert", "update", "delete", "drop", "alter", "truncate",
                     "create", "replace", "grant", "revoke")


def _is_safe_select(sql: str) -> bool:
    """
    Return True if *sql* is a pure SELECT statement.

    Rejects queries that contain any data-modifying or DDL keywords,
    regardless of case.  This is a simple string-based guard — not a full
    SQL parser — but sufficient to prevent accidental data loss from an AI
    hallucinating a DROP TABLE.
    """
    # Normalise to lowercase for case-insensitive comparison.
    sql_lower = sql.lower()

    # Must start with SELECT (after stripping leading whitespace/comments).
    if not sql_lower.lstrip().startswith("select"):
        return False

    # Reject if any blocked keyword appears anywhere in the query.
    for keyword in _BLOCKED_KEYWORDS:
        # Use word-boundary matching so e.g. "deleted_at" doesn't trigger.
        if re.search(rf"\b{keyword}\b", sql_lower):
            return False

    return True


# ---------------------------------------------------------------------------
# 5. SQL clean-up helper
# ---------------------------------------------------------------------------

def _strip_markdown(text: str) -> str:
    """
    Remove markdown code fences that Gemini sometimes adds around SQL.

    Handles:
        ```sql
        SELECT ...
        ```
    and bare triple-backtick blocks.
    """
    # Remove ```sql ... ``` or ``` ... ``` fences.
    text = re.sub(r"```(?:sql)?\s*", "", text, flags=re.IGNORECASE)
    text = text.replace("```", "")
    return text.strip()


# ---------------------------------------------------------------------------
# 6. Main function: ask_copilot
# ---------------------------------------------------------------------------

def ask_copilot(user_question: str) -> str:
    """
    Answer a natural-language question about the LedgerMind invoices data.

    Parameters
    ----------
    user_question : str
        A plain-English question, e.g. "How many invoices are unmatched?"

    Returns
    -------
    str
        A concise, human-readable answer.  On error, returns a safe
        fallback message instead of raising an exception.
    """

    # --- Guard: missing API key -------------------------------------------
    if not _client:
        return (
            "[Copilot unavailable] GEMINI_API_KEY is not set in .env. "
            "Please add a valid key and restart."
        )

    # =========================================================================
    # PASS 1: Natural language → SQL query
    # =========================================================================

    # --- Step 1a: Build the SQL-generation prompt -------------------------
    # We give Gemini the full table schema plus strict instructions so it
    # returns a bare SQL string rather than an explanation or prose.
    sql_prompt = f"""You are a SQL expert working with a SQLite/PostgreSQL database.

Here is the database schema:
{TABLE_SCHEMA}

The user asks: "{user_question}"

Return ONLY a valid SQL SELECT query that answers the question.
Rules:
- No explanation, no markdown, no code fences.
- Only use the table and columns listed above.
- If the question cannot be answered with a SELECT query, return exactly: UNSUPPORTED
"""

    # --- Step 1b: Call Gemini for the SQL query ---------------------------
    try:
        raw_sql = _generate_content_with_fallback(sql_prompt)
    except Exception as e:
        return f"[Copilot error] Could not generate SQL query.\nReason: {e}"

    # --- Step 1c: Handle unsupported questions ----------------------------
    if raw_sql.strip().upper() == "UNSUPPORTED":
        return (
            "I can only answer questions about your invoices data "
            "(e.g. counts, amounts, statuses). Please rephrase your question."
        )

    # --- Step 1d: Strip any markdown fences Gemini may have added ---------
    clean_sql = _strip_markdown(raw_sql)

    # --- Step 1e: Safety check — only SELECT is allowed ------------------
    if not _is_safe_select(clean_sql):
        return (
            f"[Security block] The generated query contains disallowed "
            f"operations and was not executed.\nGenerated: {clean_sql}"
        )

    # =========================================================================
    # PASS 2: Execute SQL → convert results to human-readable answer
    # =========================================================================

    # --- Step 2a: Run the query against the database ----------------------
    try:
        import pandas as pd
        from backend.db import get_engine
        from sqlalchemy import text

        engine = get_engine()

        with engine.connect() as conn:
            result_df = pd.read_sql(text(clean_sql), conn)

    except Exception as e:
        return (
            f"[Query error] The SQL query could not be executed.\n"
            f"SQL: {clean_sql}\n"
            f"Reason: {e}"
        )

    # --- Step 2b: Handle empty result sets --------------------------------
    if result_df.empty:
        return "No data found for your question. The table may be empty."

    # --- Step 2c: Serialise the DataFrame to a readable string for Gemini --
    # We convert to a simple CSV-like text — small enough to fit in a prompt.
    data_as_text = result_df.to_string(index=False)

    # --- Step 2d: Build the answer-generation prompt ----------------------
    answer_prompt = f"""You are LedgerMind AI, a helpful financial assistant.

The user asked: "{user_question}"

A SQL query was run against the invoices database and returned this data:
{data_as_text}

Convert this data into a short, clear, human-readable answer.
- Be concise (2-4 sentences max).
- Use plain English, not SQL or technical jargon.
- If amounts are involved, format them with a $ sign and commas.
"""

    # --- Step 2e: Call Gemini to generate the final human answer ----------
    try:
        return _generate_content_with_fallback(answer_prompt)

    except Exception as e:
        # If the second Gemini call fails, fall back to showing the raw data.
        return (
            f"Here is the raw data for your question:\n\n"
            f"{data_as_text}\n\n"
            f"(Could not generate a summary: {e})"
        )


# ---------------------------------------------------------------------------
# Quick self-test — run with:  python -m backend.copilot_agent
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    if sys.stdout.encoding != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")

    # Sample questions to exercise the copilot end-to-end.
    test_questions = [
        "How many invoices are unmatched?",
        "What is the total amount of matched invoices?",
        "Show me all unmatched invoices with their explanations.",
        "Which invoice has the highest amount?",
    ]

    print("=" * 60)
    print("  LedgerMind Copilot — Self Test")
    print("=" * 60)

    for question in test_questions:
        print(f"\n❓ {question}")
        print("-" * 60)
        answer = ask_copilot(question)
        print(answer)
        print()
