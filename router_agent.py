"""
router_agent.py
===============
Top-level entry point for router_agent.
"""

import sys
import os

# Ensure UTF-8 output on Windows consoles
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

# Ensure project root is in sys.path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.router_agent import route_and_answer

if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        result = route_and_answer(query)
        print(f"Route: {result['route']}")
        print(f"Answer: {result['answer']}")
    else:
        questions = [
            "How many invoices are unmatched?",
            "What is the standard settlement cycle for merchants?",
            "What is the refund policy?",
            "What is the total amount of matched invoices?",
        ]
        for q in questions:
            res = route_and_answer(q)
            print(f"\n❓ {res['question']}")
            print(f"🔀 Route : [{res['route']}]")
            print(f"💬 Answer: {res['answer']}\n")
            print("-" * 60)
