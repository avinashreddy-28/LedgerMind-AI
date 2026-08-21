"""
exception_agent.py
===================
AI-powered exception analysis for unmatched invoices.

Uses Google Gemini to generate concise, human-readable explanations
for why an invoice might not have a matching bank transaction.

Usage:
    from backend.exception_agent import explain_exception
    explanation = explain_exception("INV003", 7000)
    print(explanation)
"""

import os
import sys

# ---------------------------------------------------------------------------
# 1. Load environment variables from the .env file at the project root.
# ---------------------------------------------------------------------------
from dotenv import load_dotenv

# Resolve the project root (one level up from backend/).
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(project_root, ".env")

# Inject .env key-value pairs into os.environ.
load_dotenv(dotenv_path)

# ---------------------------------------------------------------------------
# 2. Retrieve the API key.
# ---------------------------------------------------------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ---------------------------------------------------------------------------
# 3. Configure the Gemini client (once, at module load time).
# ---------------------------------------------------------------------------
from google import genai

# Create a reusable client instance.  If the key is missing the function
# will return a graceful fallback message instead of crashing.
_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

# The model to use for generating explanations.
MODEL_NAME = "gemini-3.6-flash"


# ---------------------------------------------------------------------------
# 4. Main function: explain_exception
# ---------------------------------------------------------------------------

def explain_exception(invoice_id: str, amount: float) -> str:
    """
    Ask Gemini why an invoice might not have a matching bank transaction.

    Parameters
    ----------
    invoice_id : str
        The identifier of the unmatched invoice (e.g. "INV003").
    amount : float
        The invoice amount that had no corresponding bank entry.

    Returns
    -------
    str
        A plain-text explanation listing 2-4 possible reasons for the
        mismatch.  If the API call fails for any reason, a safe fallback
        message is returned instead of raising an exception.
    """

    # --- Guard: missing API key -------------------------------------------
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your_key_here":
        return (
            f"[API key not configured] Unable to analyse invoice {invoice_id}. "
            "Please set a valid GEMINI_API_KEY in your .env file."
        )

    # --- Build the prompt -------------------------------------------------
    # We give Gemini enough context about the situation and ask for a concise,
    # numbered list so the output is easy to read in a dashboard card.
    prompt = (
        f"You are LedgerMind AI, an intelligent accounting assistant.\n\n"
        f"During bank reconciliation, invoice **{invoice_id}** with amount "
        f"**{amount:,.2f}** could not be matched to any bank transaction.\n\n"
        f"List 2-4 concise possible reasons why this invoice has no matching "
        f"bank entry. Keep each reason to one sentence. "
        f"Format as a numbered list."
    )

    # --- Call the Gemini API ----------------------------------------------
    try:
        response = _client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )

        # Extract and return the plain-text reply.
        return response.text

    except Exception as e:
        # --- Graceful error handling --------------------------------------
        # If the API is down, the key is invalid, or any other error occurs,
        # we return a human-readable fallback rather than crashing the app.
        return (
            f"[AI analysis unavailable] Could not generate explanation for "
            f"invoice {invoice_id} (amount: {amount:,.2f}).\n"
            f"Reason: {str(e)}"
        )


# ---------------------------------------------------------------------------
# Quick self-test — run with:  python -m backend.exception_agent
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Set UTF-8 encoding for Windows console output.
    if sys.stdout.encoding != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")

    print("Testing explain_exception with a sample unmatched invoice...\n")

    result = explain_exception("INV003", 7000)
    print(result)
