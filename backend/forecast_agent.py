"""
backend/forecast_agent.py — Revenue Forecasting & AI Analysis Agent
===================================================================
Uses scikit-learn LinearRegression to forecast future revenue based on
historical trends, and invokes Gemini to generate concise business insights.
"""

import os
import sys
from typing import Dict, List, Tuple, Union
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from dotenv import load_dotenv

# Ensure UTF-8 output on Windows consoles
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------------------
# 1. Environment & Gemini Configuration
# ---------------------------------------------------------------------------
# Load environment variables (.env) from the project root
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
load_dotenv(dotenv_path)

from google import genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

# Candidate models in order of preference for rate-limit resilience
CANDIDATE_MODELS = ["gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.5-flash-lite"]

# Calendar month sequence for label generation
MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def _generate_content_with_fallback(contents: str) -> str:
    """
    Attempts generation with the primary Gemini model, falling back to
    alternative models if 429 quota or rate limits are encountered.
    """
    if not _client:
        return "Gemini API key is not configured in .env."

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
    raise last_err or RuntimeError("No Gemini models available.")


# ---------------------------------------------------------------------------
# 2. Forecasting Function: forecast_revenue
# ---------------------------------------------------------------------------
def forecast_revenue(csv_path: str = "data/revenue.csv", months_ahead: int = 3) -> pd.DataFrame:
    """
    Fit a Linear Regression model on historical revenue data and predict
    revenue for the next `months_ahead` periods.

    Parameters
    ----------
    csv_path : str
        Path to the CSV file containing 'month' and 'revenue' columns.
    months_ahead : int, default=3
        Number of future months to forecast.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns ['month', 'predicted_revenue'].
    """
    # Step 1: Load revenue CSV with pandas
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Revenue CSV file not found at: {csv_path}")

    df = pd.read_csv(csv_path)

    if "month" not in df.columns or "revenue" not in df.columns:
        raise ValueError("CSV must contain 'month' and 'revenue' columns.")

    # Step 2: Convert month names to numeric index (1, 2, 3, ...) as feature X
    # X shape must be (N, 1) for scikit-learn
    n_samples = len(df)
    X = np.arange(1, n_samples + 1).reshape(-1, 1)
    
    # Step 3: Target y is the historical revenue values
    y = df["revenue"].values

    # Step 4: Fit LinearRegression model
    model = LinearRegression()
    model.fit(X, y)

    # Step 5: Predict for future periods: [n_samples + 1, ..., n_samples + months_ahead]
    future_X = np.arange(n_samples + 1, n_samples + months_ahead + 1).reshape(-1, 1)
    raw_predictions = model.predict(future_X)

    # Step 6: Generate labels for future months
    # Find the index of the last month in MONTH_NAMES if recognized, else extrapolate
    last_month_name = str(df["month"].iloc[-1]).strip()
    if last_month_name in MONTH_NAMES:
        last_idx = MONTH_NAMES.index(last_month_name)
        future_months = [MONTH_NAMES[(last_idx + i + 1) % 12] for i in range(months_ahead)]
    else:
        # Fallback to Month N+1, Month N+2...
        future_months = [f"Month {n_samples + i + 1}" for i in range(months_ahead)]

    # Step 7: Round predictions to the nearest integer
    rounded_predictions = [int(round(val)) for val in raw_predictions]

    # Step 8: Construct and return the result DataFrame
    forecast_df = pd.DataFrame({
        "month": future_months,
        "predicted_revenue": rounded_predictions
    })

    return forecast_df


# ---------------------------------------------------------------------------
# 3. AI Commentary Function: explain_forecast
# ---------------------------------------------------------------------------
def explain_forecast(historical_df: pd.DataFrame, predicted_df: pd.DataFrame) -> str:
    """
    Construct a prompt with historical and predicted revenue data, then
    ask Gemini for a concise 3-4 sentence executive financial commentary.

    Parameters
    ----------
    historical_df : pd.DataFrame
        DataFrame with historical ['month', 'revenue'] data.
    predicted_df : pd.DataFrame
        DataFrame with forecasted ['month', 'predicted_revenue'] data.

    Returns
    -------
    str
        AI-generated executive commentary.
    """
    # Step 1: Serialize historical and forecasted data to formatted text
    hist_text = "\n".join(
        [f"  - {row['month']}: ${row['revenue']:,}" for _, row in historical_df.iterrows()]
    )
    pred_text = "\n".join(
        [f"  - {row['month']}: ${row['predicted_revenue']:,} (Projected)" for _, row in predicted_df.iterrows()]
    )

    # Step 2: Build the prompt for Gemini
    prompt = f"""You are LedgerMind AI, a senior corporate financial analyst.

Review the following historical monthly revenue and the linear regression forecast for the upcoming quarter:

Historical Monthly Revenue:
{hist_text}

Forecasted Revenue (Next 3 Months):
{pred_text}

Provide a concise, professional, executive-level summary (3 to 4 sentences max):
1. Identify the overall revenue trend direction (e.g., steady growth, acceleration).
2. Quantify the estimated monthly growth rate / trajectory.
3. Highlight any key business observations or strategic recommendations based on this forecast.

Write directly in clear, professional English without preamble.
"""

    # Step 3: Send prompt to Gemini with multi-model fallback
    try:
        commentary = _generate_content_with_fallback(prompt)
        return commentary
    except Exception as e:
        return (
            f"Historical revenue grew from ${historical_df['revenue'].iloc[0]:,} to "
            f"${historical_df['revenue'].iloc[-1]:,}. Projected revenue continues an upward trajectory "
            f"reaching ${predicted_df['predicted_revenue'].iloc[-1]:,} by {predicted_df['month'].iloc[-1]}. "
            f"(AI commentary fallback: {e})"
        )


# ---------------------------------------------------------------------------
# 4. Standalone Runner / Self-Test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    revenue_csv = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "revenue.csv")
    print("=" * 60)
    print("  LedgerMind AI — Forecast Agent Standalone Test")
    print("=" * 60)

    # 1. Forecast revenue
    hist_df = pd.read_csv(revenue_csv)
    pred_df = forecast_revenue(revenue_csv, months_ahead=3)
    
    print("\n📈 Historical Revenue:")
    for _, r in hist_df.iterrows():
        print(f"   {r['month']}: ${r['revenue']:,}")

    print("\n🔮 Predicted Revenue (Next 3 Months):")
    for _, r in pred_df.iterrows():
        print(f"   {r['month']}: ${r['predicted_revenue']:,}")

    # 2. Generate AI Commentary
    print("\n🤖 AI Forecast Commentary:")
    print("-" * 60)
    summary = explain_forecast(hist_df, pred_df)
    print(summary)
    print("=" * 60)
