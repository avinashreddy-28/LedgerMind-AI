"""
router_agent.py — Intelligent Query Routing Agent
=================================================
Routes incoming user queries to either:
1. SQL Copilot Agent (`DATA`): For invoice database queries (amounts, counts, statuses).
2. RAG Policy Agent (`POLICY`): For operational rules, settlement/refund policies, manuals.

Public API:
    route_and_answer(user_question: str) -> dict
    # Returns: {"route": "DATA" | "POLICY", "answer": str}
"""

import os
import re
import sys
from dotenv import load_dotenv

# Ensure UTF-8 output on Windows consoles
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------------------
# 1. Environment & Path Setup
# ---------------------------------------------------------------------------
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

dotenv_path = os.path.join(project_root, ".env")
load_dotenv(dotenv_path)

# ---------------------------------------------------------------------------
# 2. Configure Gemini Client for Query Classification
# ---------------------------------------------------------------------------
from google import genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
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

# Import specialized downstream agents
from backend.copilot_agent import ask_copilot
from backend.rag_agent import answer_policy_question


# ---------------------------------------------------------------------------
# 3. Router Function: route_and_answer
# ---------------------------------------------------------------------------
def route_and_answer(user_question: str) -> dict:
    """
    Classify the user question as DATA or POLICY, invoke the appropriate
    downstream agent, and return both the answer and the selected route.

    Parameters
    ----------
    user_question : str
        The question asked by the user.

    Returns
    -------
    dict
        {
            "route": "DATA" | "POLICY",
            "question": str,
            "answer": str
        }
    """
    # Guard: Missing Gemini API key
    if not _client:
        return {
            "route": "UNKNOWN",
            "question": user_question,
            "answer": "[Router error] GEMINI_API_KEY is not configured in .env."
        }

    # -----------------------------------------------------------------------
    # Step 1: Query Classification Prompt
    # -----------------------------------------------------------------------
    classification_prompt = f"""Classify this question as either DATA (about invoices, amounts, matched/unmatched status - specific numbers from a database) or POLICY (about rules, cycles, procedures, general knowledge).
Respond with ONLY the word DATA or POLICY.

Question: "{user_question}"
"""

    # -----------------------------------------------------------------------
    # Step 2: Send Classification Request to Gemini
    # -----------------------------------------------------------------------
    try:
        raw_classification = _generate_content_with_fallback(classification_prompt).upper()
    except Exception as e:
        # Fallback heuristic if classification call fails
        raw_classification = "DATA" if any(w in user_question.lower() for w in ["invoice", "amount", "matched", "unmatched", "count", "sum"]) else "POLICY"

    # Normalize category to DATA or POLICY
    if "DATA" in raw_classification:
        route = "DATA"
    elif "POLICY" in raw_classification:
        route = "POLICY"
    else:
        route = "DATA"

    # -----------------------------------------------------------------------
    # Step 3: Dispatch to the designated agent
    # -----------------------------------------------------------------------
    if route == "DATA":
        # Route to Text-to-SQL Copilot Agent
        answer = ask_copilot(user_question)
    else:
        # Route to RAG Policy Agent
        answer = answer_policy_question(user_question)

    return {
        "route": route,
        "question": user_question,
        "answer": answer
    }


# ---------------------------------------------------------------------------
# Quick standalone test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    sample_queries = [
        "How many invoices are unmatched?",
        "What is the standard settlement cycle for merchants?",
        "What is the total amount of matched invoices?",
        "What is the refund processing policy?",
        "Which invoices require escalation?"
    ]

    print("=" * 60)
    print("  LedgerMind AI — Router Agent Self Test")
    print("=" * 60)

    for q in sample_queries:
        res = route_and_answer(q)
        print(f"\n❓ Question: {res['question']}")
        print(f"🔀 Route   : [{res['route']}]")
        print(f"💬 Answer  :\n{res['answer']}")
        print("-" * 60)
