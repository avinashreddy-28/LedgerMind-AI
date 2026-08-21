"""
test_gemini.py
==============
Quick smoke-test to verify the Gemini API key is working.

Loads GEMINI_API_KEY from the project-root .env file, sends a simple
prompt to Gemini, and prints the response.

Usage:
    python backend/test_gemini.py
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

# load_dotenv reads key=value pairs from .env and injects them into
# os.environ so the rest of the code can access them normally.
load_dotenv(dotenv_path)

# ---------------------------------------------------------------------------
# 2. Retrieve and validate the API key.
# ---------------------------------------------------------------------------
api_key = os.getenv("GEMINI_API_KEY")

if not api_key or api_key == "your_key_here":
    print("❌ ERROR: Please set a valid GEMINI_API_KEY in your .env file.")
    print(f"   .env location: {dotenv_path}")
    sys.exit(1)

print(f"✅ API key loaded (ends with ...{api_key[-4:]})")

# ---------------------------------------------------------------------------
# 3. Configure the Gemini client.
# ---------------------------------------------------------------------------
from google import genai

# Create a client instance with the API key.
client = genai.Client(api_key=api_key)

# ---------------------------------------------------------------------------
# 4. Send a test prompt to Gemini.
# ---------------------------------------------------------------------------
# Try gemini-2.5-pro first; fall back to gemini-2.0-flash if unavailable.
test_prompt = (
    "You are LedgerMind AI, an intelligent accounting assistant. "
    "Say hello and briefly describe what you can do in 2-3 sentences."
)

models_to_try = ["gemini-3.6-flash", "gemini-3.5-flash-lite"]

for model_name in models_to_try:
    try:
        print(f"\n🔄 Trying model: {model_name} ...")
        response = client.models.generate_content(
            model=model_name,
            contents=test_prompt,
        )
        # Print the model's reply.
        print(f"✅ Model: {model_name}")
        print(f"\n📝 Response:\n{response.text}")
        break  # Success — no need to try the next model.

    except Exception as e:
        print(f"⚠️  {model_name} failed: {e}")
        if model_name == models_to_try[-1]:
            # All models exhausted.
            print("\n❌ All models failed. Check your API key and quota.")
            sys.exit(1)
        print("   Falling back to the next model...")
