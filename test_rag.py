"""
test_rag.py — Standalone Test for RAG Retrieval & Policy Q&A
============================================================
Tests:
1. retrieve_context() retrieval from ChromaDB.
2. answer_policy_question() with Gemini grounded response.
"""

import sys
import os

# Ensure UTF-8 output on Windows consoles
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

# Ensure project root is on sys.path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.rag_agent import retrieve_context, answer_policy_question

print("=" * 60)
print("  LedgerMind AI — RAG Agent Standalone Tests")
print("=" * 60)

# ---------------------------------------------------------------------------
# Test 1: retrieve_context
# ---------------------------------------------------------------------------
query1 = "What is the settlement cycle?"
print(f"\n🔍 [Test 1] retrieve_context('{query1}')")
print("-" * 60)
chunks = retrieve_context(query1, n_results=3)

for idx, chunk in enumerate(chunks, 1):
    print(f"\n📄 Chunk #{idx}:")
    print(chunk)

# ---------------------------------------------------------------------------
# Test 2: answer_policy_question with document-backed question
# ---------------------------------------------------------------------------
query2 = "What is the settlement cycle and when are settlements processed?"
print(f"\n\n🤖 [Test 2] answer_policy_question('{query2}')")
print("-" * 60)
answer2 = answer_policy_question(query2)
print(answer2)

# ---------------------------------------------------------------------------
# Test 3: answer_policy_question with specific/out-of-scope question
# ---------------------------------------------------------------------------
query3 = "What is Razorpay's settlement cycle?"
print(f"\n\n🤖 [Test 3] answer_policy_question('{query3}')")
print("-" * 60)
answer3 = answer_policy_question(query3)
print(answer3)

# ---------------------------------------------------------------------------
# Test 4: answer_policy_question for refund policy
# ---------------------------------------------------------------------------
query4 = "How are refunds handled and who approves partial refunds?"
print(f"\n\n🤖 [Test 4] answer_policy_question('{query4}')")
print("-" * 60)
answer4 = answer_policy_question(query4)
print(answer4)

print("\n" + "=" * 60)
print("  RAG Tests Complete.")
print("=" * 60)
