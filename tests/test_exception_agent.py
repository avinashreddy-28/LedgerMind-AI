"""
test_exception_agent.py
========================
Quick test to verify the AI-powered exception agent.

Calls explain_exception with a sample unmatched invoice
and prints the Gemini-generated explanation.
"""

import os
import sys

# Ensure the project root is on the Python path.
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Fix encoding for Windows console.
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

from backend.exception_agent import explain_exception

# Call the exception agent with a sample unmatched invoice.
print("=" * 50)
print("  EXCEPTION AGENT TEST")
print("=" * 50)
print(f"\nInvoice ID : INV003")
print(f"Amount     : 7,000\n")
print("-" * 50)

explanation = explain_exception("INV003", 7000)
print(explanation)

print("-" * 50)
