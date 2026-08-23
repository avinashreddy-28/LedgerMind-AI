"""
test_copilot.py
===============
Quick test for the three copilot questions.
Run with: python test_copilot.py
"""

import sys
import os

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.copilot_agent import ask_copilot

questions = [
    "Which invoices are unmatched?",
    "What is the total amount of matched invoices?",
    "How many invoices do we have in total?",
]

print("=" * 60)
print("  LedgerMind Copilot — Question Tests")
print("=" * 60)

for q in questions:
    print(f"\n❓ {q}")
    print("-" * 60)
    answer = ask_copilot(q)
    print(answer)

print("\n" + "=" * 60)
print("  Done.")
