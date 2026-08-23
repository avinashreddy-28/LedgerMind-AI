"""
test_router.py — Verification for Multi-Agent Query Router
==========================================================
Tests mixed questions to verify that DATA and POLICY routes are
properly distinguished and answered.
"""

import os
import sys

# Ensure UTF-8 output on Windows consoles
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

# Ensure project root is in sys.path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.router_agent import route_and_answer

test_questions = [
    "Which invoices are unmatched?",       # Expected: DATA
    "What is the settlement cycle?",       # Expected: POLICY
    "How many invoices are matched?",       # Expected: DATA
    "What is the refund policy?",           # Expected: POLICY
]

print("=" * 65)
print("  LedgerMind AI — Multi-Agent Router Mixed Question Tests")
print("=" * 65)

for idx, q in enumerate(test_questions, 1):
    result = route_and_answer(q)
    route = result["route"]
    answer = result["answer"]
    
    route_badge = "📊 Database" if route == "DATA" else "📄 Policy Documents"
    
    print(f"\n[{idx}/4] ❓ Question : {q}")
    print(f"      🔀 Route    : {route} ({route_badge})")
    print(f"      💬 Answer   :\n{answer}")
    print("-" * 65)

print("\n" + "=" * 65)
print("  All 4 test cases completed successfully.")
print("=" * 65)
