"""
app.py — LedgerMind-AI Streamlit Dashboard
===========================================
Upload invoice and bank CSVs, run reconciliation, and view
matched / unmatched invoices alongside key metrics. Allows
generating AI-powered explanations for unmatched entries.

Launch with:
    streamlit run frontend/app.py
"""

import sys
import os
import time

# ---------------------------------------------------------------------------
# Make the project root importable so we can use backend.reconciliation
# regardless of which directory Streamlit is launched from.
# ---------------------------------------------------------------------------
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import streamlit as st
import pandas as pd
from backend.reconciliation import load_data, reconcile_transactions, generate_exceptions

# ---------------------------------------------------------------------------
# Page configuration — must be the first Streamlit command.
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="LedgerMind AI — Reconciliation",
    page_icon="📒",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Custom CSS — premium dark-accented look with glassmorphism cards.
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* ---------- Google Font ---------- */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    /* ---------- Global ---------- */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ---------- Header banner ---------- */
    .main-header {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        padding: 2.5rem 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35);
    }
    .main-header h1 {
        color: #ffffff;
        font-weight: 800;
        font-size: 2.2rem;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .main-header p {
        color: #a5b4fc;
        font-size: 1.05rem;
        margin: 0.5rem 0 0;
    }

    /* ---------- Metric cards ---------- */
    .metric-row {
        display: flex;
        gap: 1.25rem;
        margin-bottom: 1.75rem;
        flex-wrap: wrap;
    }
    .metric-card {
        flex: 1 1 200px;
        background: rgba(255, 255, 255, 0.06);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 14px;
        padding: 1.5rem 1.75rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 30px rgba(99, 102, 241, 0.25);
    }
    .metric-card .label {
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        color: #94a3b8;
        margin-bottom: 0.35rem;
    }
    .metric-card .value {
        font-size: 2rem;
        font-weight: 700;
        color: #e2e8f0;
    }
    .metric-card .value.green  { color: #34d399; }
    .metric-card .value.red    { color: #f87171; }
    .metric-card .value.purple { color: #a78bfa; }
    .metric-card .value.blue   { color: #60a5fa; }

    /* ---------- Section titles ---------- */
    .section-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #e2e8f0;
        margin: 1.5rem 0 0.75rem;
        padding-bottom: 0.4rem;
        border-bottom: 2px solid rgba(99, 102, 241, 0.4);
        display: inline-block;
    }

    /* ---------- Upload area ---------- */
    .upload-section {
        background: rgba(255, 255, 255, 0.04);
        border: 1px dashed rgba(255, 255, 255, 0.15);
        border-radius: 14px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }

    /* ---------- Tables ---------- */
    .stDataFrame { border-radius: 10px; overflow: hidden; }

    /* ---------- Button override ---------- */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: #ffffff;
        border: none;
        border-radius: 10px;
        padding: 0.65rem 2.5rem;
        font-weight: 600;
        font-size: 1rem;
        letter-spacing: 0.3px;
        transition: all 0.25s ease;
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.4);
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #818cf8, #a78bfa);
        box-shadow: 0 6px 24px rgba(139, 92, 246, 0.5);
        transform: translateY(-2px);
    }

    /* ---------- AI Card (inside expanders) ---------- */
    .ai-card {
        background: rgba(99, 102, 241, 0.08);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 12px;
        padding: 1.25rem;
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .ai-card-title {
        font-weight: 700;
        color: #a5b4fc;
        margin-bottom: 0.5rem;
    }
    .ai-badge {
        display: inline-block;
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: #fff;
        padding: 0.2rem 0.7rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-left: 0.5rem;
        vertical-align: middle;
    }

    /* ---------- Footer ---------- */
    .footer {
        text-align: center;
        color: #64748b;
        font-size: 0.8rem;
        margin-top: 3rem;
        padding: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="main-header">
        <h1>📒 LedgerMind AI</h1>
        <p>Intelligent Invoice &amp; Bank Reconciliation Dashboard</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# State Initialization
# ---------------------------------------------------------------------------
if "recon_results" not in st.session_state:
    st.session_state.recon_results = None
if "invoice_df" not in st.session_state:
    st.session_state.invoice_df = None
if "bank_df" not in st.session_state:
    st.session_state.bank_df = None
if "ai_explanations" not in st.session_state:
    st.session_state.ai_explanations = None

# ---------------------------------------------------------------------------
# File uploaders — two-column layout
# ---------------------------------------------------------------------------
col_inv, col_bank = st.columns(2)

with col_inv:
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    st.markdown("##### 📄 Invoice CSV")
    invoice_file = st.file_uploader(
        "Upload your invoice CSV",
        type=["csv"],
        key="invoice_uploader",
        label_visibility="collapsed",
    )
    st.markdown("</div>", unsafe_allow_html=True)

with col_bank:
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    st.markdown("##### 🏦 Bank Statement CSV")
    bank_file = st.file_uploader(
        "Upload your bank statement CSV",
        type=["csv"],
        key="bank_uploader",
        label_visibility="collapsed",
    )
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Reconciliation trigger
# ---------------------------------------------------------------------------
run_btn = st.button("🚀  Run Reconciliation", use_container_width=True)

if run_btn:
    # ---- Validate uploads -------------------------------------------------
    if invoice_file is None or bank_file is None:
        st.warning("⚠️  Please upload **both** CSV files before running.")
        st.stop()

    # ---- Load data from the uploaded files --------------------------------
    invoice_df = pd.read_csv(invoice_file)
    bank_df = pd.read_csv(bank_file)

    # Clean column names & string values.
    for df in (invoice_df, bank_df):
        df.columns = df.columns.str.strip()
        for col in df.select_dtypes("object").columns:
            df[col] = df[col].str.strip()

    # ---- Run reconciliation -----------------------------------------------
    results = reconcile_transactions(invoice_df, bank_df)

    # Store reconciliation results in session state.
    st.session_state.recon_results = results
    st.session_state.invoice_df = invoice_df
    st.session_state.bank_df = bank_df

    # ---- Auto-generate AI exceptions for unmatched invoices ---------------
    unmatched = results["unmatched"]
    if not unmatched.empty:
        with st.spinner(
            f"🤖 Analysing {len(unmatched)} unmatched invoice(s) with Gemini AI…"
        ):
            ex_df = generate_exceptions(unmatched)
            st.session_state.ai_explanations = ex_df
    else:
        st.session_state.ai_explanations = None

# ---------------------------------------------------------------------------
# Display Results
# ---------------------------------------------------------------------------
if st.session_state.recon_results is not None:
    results = st.session_state.recon_results
    invoice_df = st.session_state.invoice_df
    matched_df = results["matched"]
    unmatched_df = results["unmatched"]
    match_pct = results["match_percentage"]

    # ---- Metric cards -----------------------------------------------------
    st.markdown(
        f"""
        <div class="metric-row">
            <div class="metric-card">
                <div class="label">Total Invoices</div>
                <div class="value blue">{len(invoice_df)}</div>
            </div>
            <div class="metric-card">
                <div class="label">Matched</div>
                <div class="value green">{len(matched_df)}</div>
            </div>
            <div class="metric-card">
                <div class="label">Unmatched</div>
                <div class="value red">{len(unmatched_df)}</div>
            </div>
            <div class="metric-card">
                <div class="label">Match %</div>
                <div class="value purple">{match_pct}%</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---- Data tables ------------------------------------------------------
    tab_matched, tab_unmatched, tab_all = st.tabs(
        ["✅ Matched Invoices", "❌ Unmatched Invoices", "📋 All Invoices"]
    )

    with tab_matched:
        if matched_df.empty:
            st.info("No matched invoices found.")
        else:
            st.dataframe(matched_df, use_container_width=True, hide_index=True)

    with tab_unmatched:
        if unmatched_df.empty:
            st.success("🎉 All invoices matched — nothing to report!")
        else:
            st.write("The following invoices did not match any bank statement entries:")
            st.dataframe(unmatched_df, use_container_width=True, hide_index=True)

    with tab_all:
        st.dataframe(invoice_df, use_container_width=True, hide_index=True)

    # ======================================================================
    # AI EXCEPTION ANALYSIS — Standalone section after the tabs
    # ======================================================================
    if not unmatched_df.empty:
        st.markdown("---")
        st.markdown(
            '<div class="section-title">🤖 AI Exception Analysis</div>',
            unsafe_allow_html=True,
        )

        if st.session_state.ai_explanations is not None:
            ex_df = st.session_state.ai_explanations

            st.caption(
                f"Gemini analysed **{len(ex_df)}** unmatched invoice(s). "
                "Expand each card below for details."
            )

            for _, row in ex_df.iterrows():
                inv_id = row["invoice_id"]
                amt = row["amount"]
                explanation = row["explanation"]

                with st.expander(
                    f"📌  {inv_id}  —  ${amt:,.2f}",
                    expanded=False,
                ):
                    st.markdown(
                        f"""
                        <div class="ai-card">
                            <div class="ai-card-title">
                                Invoice {inv_id}
                                <span class="ai-badge">AI Generated</span>
                            </div>
                            <div><strong>Amount:</strong> ${amt:,.2f}</div>
                            <br/>
                            <div>{explanation}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            # Re-run button to refresh AI analysis.
            st.write("")
            col_rerun, _ = st.columns([1, 3])
            with col_rerun:
                if st.button("🔄  Re-analyse with AI", use_container_width=True):
                    with st.spinner("Re-analysing with Gemini…"):
                        ex_df = generate_exceptions(unmatched_df)
                        st.session_state.ai_explanations = ex_df
                        st.rerun()

        else:
            # Offer a manual trigger if auto-generation was skipped.
            st.info(
                "No AI analysis available yet. Click below to generate "
                "explanations for unmatched invoices."
            )
            if st.button(
                "🔍  Explain Mismatches with LedgerMind AI",
                use_container_width=True,
            ):
                with st.spinner(
                    f"Analysing {len(unmatched_df)} invoice(s) with Gemini…"
                ):
                    ex_df = generate_exceptions(unmatched_df)
                    st.session_state.ai_explanations = ex_df
                    st.rerun()

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown(
    '<div class="footer">Built with ❤️ by LedgerMind AI · Powered by Streamlit</div>',
    unsafe_allow_html=True,
)
