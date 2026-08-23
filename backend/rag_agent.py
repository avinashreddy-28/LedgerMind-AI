"""
rag_agent.py — RAG Retrieval and Policy Question Answering Agent
================================================================
Retrieves relevant policy documents from ChromaDB and uses Google Gemini
to generate grounded, factual answers to financial policy questions.

Functions:
1. retrieve_context(query, n_results=3) -> list[str]
   Queries the local ChromaDB 'finance_docs' collection and returns matching text chunks.
2. answer_policy_question(user_question) -> str
   Synthesizes an answer using ONLY the retrieved document chunks.
"""

import os
import sys
import chromadb
from dotenv import load_dotenv

# Ensure UTF-8 output on Windows consoles
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------------------
# 1. Load environment variables from .env
# ---------------------------------------------------------------------------
# Resolve the project root (one level up from backend/)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(project_root, ".env")
load_dotenv(dotenv_path)

# Path to persistent ChromaDB storage
CHROMA_DB_PATH = os.path.join(project_root, "chroma_db")

# ---------------------------------------------------------------------------
# 2. Configure the Gemini Client
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


# ---------------------------------------------------------------------------
# 3. ChromaDB Client Helper
# ---------------------------------------------------------------------------
def _get_collection():
    """
    Connects to the persistent ChromaDB instance and returns the 'finance_docs' collection.
    """
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    return client.get_or_create_collection(name="finance_docs")


# ---------------------------------------------------------------------------
# 4. Retrieval Function: retrieve_context
# ---------------------------------------------------------------------------
def retrieve_context(query: str, n_results: int = 3) -> list[str]:
    """
    Retrieve the top matching document chunks from ChromaDB for a given query.

    Parameters
    ----------
    query : str
        The search query or question.
    n_results : int, default=3
        The maximum number of relevant document chunks to return.

    Returns
    -------
    list[str]
        A list of matching chunk strings.
    """
    # Connect to the persistent ChromaDB collection
    collection = _get_collection()

    # Guard: Return empty list if collection has no documents
    if collection.count() == 0:
        return []

    # Query the collection with the search text
    results = collection.query(
        query_texts=[query],
        n_results=min(n_results, collection.count())
    )

    # results['documents'] is a list of lists: [[chunk1, chunk2, ...]]
    documents = results.get("documents", [[]])
    if documents and len(documents) > 0:
        return documents[0]
    return []


# ---------------------------------------------------------------------------
# 5. Policy Answer Function: answer_policy_question
# ---------------------------------------------------------------------------
def answer_policy_question(user_question: str) -> str:
    """
    Answer a financial policy/operations question using RAG and Gemini.

    Parameters
    ----------
    user_question : str
        The policy question asked by the user.

    Returns
    -------
    str
        A factual answer grounded ONLY in the retrieved document context.
    """
    # Guard: Missing Gemini API key
    if not _client:
        return (
            "[Policy Agent unavailable] GEMINI_API_KEY is not set in .env. "
            "Please configure your API key."
        )

    # Step 1: Retrieve relevant context chunks from ChromaDB
    chunks = retrieve_context(user_question, n_results=3)

    if not chunks:
        return (
            "I don't have that information in the available documents. "
            "No matching policy documents found."
        )

    # Step 2: Combine chunks into a formatted context block
    context_text = "\n\n---\n\n".join(chunks)

    # Step 3: Build the grounded RAG prompt
    prompt = f"""You are a helpful financial operations and policy assistant for LedgerMind AI.

Context from internal policy documents:
{context_text}

User Question: "{user_question}"

Instructions:
- Answer the user's question accurately using ONLY the information provided in the context above.
- Do NOT make up or infer rules not stated in the context.
- If the context does not contain enough information to answer the question, respond with exactly:
  "I don't have that information in the available documents."
- Keep your answer clear, professional, and concise.
"""

    # Step 4: Call Gemini with fallback
    try:
        return _generate_content_with_fallback(prompt)
    except Exception as e:
        return f"[Policy Agent error] Could not generate answer: {e}"


# ---------------------------------------------------------------------------
# Quick standalone test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    test_q = "What is the settlement cycle?"
    print(f"Testing retrieve_context for: '{test_q}'")
    context = retrieve_context(test_q)
    for i, c in enumerate(context, 1):
        print(f"\n[Chunk {i}]:\n{c}")

    print("\n" + "=" * 60)
    print(f"Testing answer_policy_question for: '{test_q}'")
    ans = answer_policy_question(test_q)
    print(f"\nAnswer:\n{ans}")
