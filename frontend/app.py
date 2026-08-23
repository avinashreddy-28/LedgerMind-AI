"""
frontend/app.py — LedgerMind AI Autonomous Finance Controller Dashboard
========================================================================
A calm, minimal, fintech-grade interface for automated reconciliation,
AI exception root-cause intelligence, multi-agent query routing, and cash forecasting.
"""

import sys
import os

# ---------------------------------------------------------------------------
# Make project root importable regardless of launch directory
# ---------------------------------------------------------------------------
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Backend agent imports
from backend.reconciliation import (
    load_data,
    reconcile_transactions,
    generate_exceptions,
    save_to_db,
)
from backend.router_agent import route_and_answer
from backend.graph import run_pipeline
from backend.report_generator import generate_pdf_report
from backend.db import _active_backend, init_db

# ---------------------------------------------------------------------------
# 1. Page Configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="LedgerMind AI",
    page_icon="📒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize database backend safely
try:
    init_db()
except Exception:
    pass

# ---------------------------------------------------------------------------
# 2. Minimalist Fintech CSS Design System
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* ---------- Reset & Clutter Removal ---------- */
    #MainMenu, footer, header {
        visibility: hidden !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    html, body, [class*="css"], .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        background-color: #f8fafc !important;
        color: #0f172a !important;
        letter-spacing: -0.01em;
    }

    .block-container {
        padding-top: 1.75rem !important;
        padding-bottom: 2.5rem !important;
        max-width: 1200px !important;
    }

    /* ---------- Header Banner ---------- */
    .fintech-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.25rem 1.75rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.03);
    }
    .header-title-group h1 {
        font-size: 1.45rem;
        font-weight: 700;
        color: #0f172a;
        margin: 0;
        letter-spacing: -0.02em;
    }
    .header-title-group p {
        font-size: 0.88rem;
        color: #64748b;
        margin: 0.2rem 0 0 0;
        font-weight: 400;
    }
    .header-status-pill {
        display: flex;
        align-items: center;
        gap: 0.45rem;
        background: #f1f5f9;
        border: 1px solid #e2e8f0;
        border-radius: 9999px;
        padding: 0.35rem 0.85rem;
        font-size: 0.78rem;
        font-weight: 600;
        color: #334155;
    }
    .status-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background-color: #10b981;
    }

    /* ---------- Cards & Containers ---------- */
    .fintech-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.4rem 1.6rem;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.03);
        margin-bottom: 1.25rem;
        animation: fadeIn 0.25s ease-in-out;
    }
    .fintech-card-header {
        font-size: 0.95rem;
        font-weight: 600;
        color: #0f172a;
        margin-bottom: 0.75rem;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(3px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* ---------- Metric Tiles ---------- */
    [data-testid="stMetric"] {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 1rem 1.25rem !important;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.03) !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    [data-testid="stMetric"]:hover {
        border-color: #cbd5e1 !important;
        box-shadow: 0 4px 12px 0 rgba(0, 0, 0, 0.05) !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        color: #64748b !important;
        text-transform: uppercase !important;
        letter-spacing: 0.04em !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.7rem !important;
        font-weight: 700 !important;
        color: #0f172a !important;
    }

    /* ---------- Sidebar ---------- */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e2e8f0 !important;
    }
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: #0f172a !important;
        font-size: 1.15rem !important;
        font-weight: 700 !important;
        margin-bottom: 0.2rem !important;
    }
    [data-testid="stSidebar"] .stMarkdown p {
        color: #64748b !important;
        font-size: 0.84rem !important;
        line-height: 1.5 !important;
    }

    /* ---------- Buttons ---------- */
    .stButton > button {
        border-radius: 10px !important;
        padding: 0.55rem 1.25rem !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        border: 1px solid #e2e8f0 !important;
        background-color: #ffffff !important;
        color: #1e293b !important;
    }
    .stButton > button:hover {
        border-color: #cbd5e1 !important;
        background-color: #f8fafc !important;
        color: #0f172a !important;
    }
    .stButton > button[kind="primary"] {
        background-color: #4f46e5 !important;
        color: #ffffff !important;
        border: none !important;
        box-shadow: 0 1px 3px rgba(79, 70, 229, 0.25) !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #4338ca !important;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3) !important;
        transform: translateY(-1px);
    }

    /* ---------- Tabs ---------- */
    [data-testid="stTabs"] {
        margin-bottom: 1.5rem !important;
    }
    [data-testid="stTabs"] button {
        font-size: 0.92rem !important;
        font-weight: 500 !important;
        color: #64748b !important;
        padding: 0.65rem 1.25rem !important;
        border-radius: 8px 8px 0 0 !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stTabs"] button[aria-selected="true"] {
        color: #4f46e5 !important;
        font-weight: 600 !important;
        border-bottom: 2px solid #4f46e5 !important;
    }

    /* ---------- Chat Messages ---------- */
    [data-testid="stChatMessage"] {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 0.85rem 1.15rem !important;
        margin-bottom: 0.65rem !important;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.02) !important;
    }

    .safety-block {
        background: #fef2f2;
        border: 1px solid #fecaca;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        color: #991b1b;
        font-size: 0.88rem;
    }

    .source-tag {
        font-size: 0.75rem;
        font-weight: 600;
        color: #64748b;
        margin-bottom: 0.35rem;
        display: inline-block;
    }

    /* ---------- DataFrames ---------- */
    .stDataFrame {
        border-radius: 10px !important;
        overflow: hidden !important;
        border: 1px solid #e2e8f0 !important;
    }

    /* ---------- Footer ---------- */
    .fintech-footer {
        text-align: center;
        color: #94a3b8;
        font-size: 0.8rem;
        margin-top: 3rem;
        padding: 1rem 0;
        border-top: 1px solid #e2e8f0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# 3. Session State Initialization
# ---------------------------------------------------------------------------
if "recon_results" not in st.session_state:
    st.session_state.recon_results = None
if "invoice_df" not in st.session_state:
    st.session_state.invoice_df = None
if "bank_df" not in st.session_state:
    st.session_state.bank_df = None
if "ai_explanations" not in st.session_state:
    st.session_state.ai_explanations = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "pipeline_result" not in st.session_state:
    st.session_state.pipeline_result = None

# ---------------------------------------------------------------------------
# 4. Sidebar Branding & System Context
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### LedgerMind")
    st.caption("Autonomous Financial Controller")
    st.write("")

    st.markdown("##### Platform")
    st.markdown(
        """
        Automates invoice-to-bank reconciliation, diagnoses mismatch root causes,
        forecasts cash flow, and answers financial queries via a multi-agent router.
        """
    )

    st.write("---")
    st.markdown("##### System Status")
    backend_label = _active_backend.capitalize() if _active_backend else "SQLite"
    st.markdown(
        f"""
        <div style="display: flex; flex-direction: column; gap: 0.4rem; font-size: 0.82rem; color: #475569;">
            <div><span style="color: #10b981; font-weight: 700;">●</span> Database: <b>{backend_label}</b></div>
            <div><span style="color: #10b981; font-weight: 700;">●</span> RAG: <b>ChromaDB Active</b></div>
            <div><span style="color: #10b981; font-weight: 700;">●</span> AI: <b>Gemini 3.7</b></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("---")
    st.caption("Version 1.0 &bull; Enterprise Ready")


# ---------------------------------------------------------------------------
# 5. Header Component
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="fintech-header">
        <div class="header-title-group">
            <h1>LedgerMind AI</h1>
            <p>An Autonomous Finance Controller for Reconciliation, Forecasting &amp; Exception Intelligence</p>
        </div>
        <div class="header-status-pill">
            <span class="status-dot"></span>
            System Active
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# 6. Tab Navigation
# ---------------------------------------------------------------------------
tab_dash, tab_copilot, tab_pipeline = st.tabs([
    "Reconciliation",
    "AI Copilot",
    "Full Pipeline",
])


# ===========================================================================
# TAB 1: RECONCILIATION DASHBOARD
# ===========================================================================
with tab_dash:
    st.markdown("##### Ingestion & Matching")

    col_inv, col_bank = st.columns(2)
    with col_inv:
        invoice_file = st.file_uploader(
            "Upload Invoices (CSV)",
            type=["csv"],
            key="dash_inv_uploader",
        )
    with col_bank:
        bank_file = st.file_uploader(
            "Upload Bank Statement (CSV)",
            type=["csv"],
            key="dash_bank_uploader",
        )

    c_rec, c_smp = st.columns([2, 1])
    with c_rec:
        reconcile_clicked = st.button("Reconcile Transactions", type="primary", use_container_width=True)
    with c_smp:
        use_default = st.button("Load Sample Data", use_container_width=True)

    if reconcile_clicked or use_default:
        try:
            if use_default or (not invoice_file and not bank_file):
                inv_path = os.path.join(project_root, "data", "invoice.csv")
                bnk_path = os.path.join(project_root, "data", "bank.csv")
            else:
                inv_path = invoice_file if invoice_file else os.path.join(project_root, "data", "invoice.csv")
                bnk_path = bank_file if bank_file else os.path.join(project_root, "data", "bank.csv")

            with st.spinner("Processing records..."):
                inv_df, bnk_df = load_data(inv_path, bnk_path)
                st.session_state.invoice_df = inv_df
                st.session_state.bank_df = bnk_df
                st.session_state.recon_results = reconcile_transactions(inv_df, bnk_df)
                st.session_state.ai_explanations = None
        except Exception as e:
            st.error(f"Reconciliation error: {e}")

    if st.session_state.recon_results is not None:
        results = st.session_state.recon_results
        matched_df = results["matched"]
        unmatched_df = results["unmatched"]
        match_pct = results["match_percentage"]
        total_inv = len(st.session_state.invoice_df) if st.session_state.invoice_df is not None else 0

        st.write("")
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Total Processed", total_inv)
        with m2:
            st.metric("Matched", len(matched_df))
        with m3:
            st.metric("Unmatched", len(unmatched_df))
        with m4:
            st.metric("Match Rate", f"{match_pct:.1f}%")

        st.write("")
        c_m, c_u = st.columns(2)
        with c_m:
            st.markdown("##### Matched Records")
            if not matched_df.empty:
                st.dataframe(matched_df, use_container_width=True, height=280)
            else:
                st.info("No matching records found.")

        with c_u:
            st.markdown("##### Exceptions (Unmatched)")
            if not unmatched_df.empty:
                st.dataframe(unmatched_df, use_container_width=True, height=280)
            else:
                st.success("All records matched.")

        if not unmatched_df.empty:
            st.write("")
            st.markdown("##### Exception Root-Cause Intelligence")
            if st.session_state.ai_explanations is None:
                if st.button("Diagnose Exceptions with AI", use_container_width=True):
                    with st.spinner("Analyzing exceptions with Gemini..."):
                        try:
                            ex_df = generate_exceptions(unmatched_df)
                            st.session_state.ai_explanations = ex_df
                            try:
                                save_to_db(matched_df, ex_df)
                            except Exception:
                                pass
                            st.rerun()
                        except Exception as e:
                            st.error(f"Exception analysis error: {e}")
            else:
                st.dataframe(st.session_state.ai_explanations, use_container_width=True)


# ===========================================================================
# TAB 2: AI COPILOT
# ===========================================================================
with tab_copilot:
    st.markdown("##### Ask LedgerMind Copilot")
    st.caption("Ask natural questions about invoice records (SQL Database) or financial policies (RAG Documents).")

    p1, p2, p3, p4 = st.columns(4)
    with p1:
        if st.button("Unmatched Invoices?", use_container_width=True):
            st.session_state._copilot_prefill = "Which invoices are unmatched?"
    with p2:
        if st.button("Total Matched Amount?", use_container_width=True):
            st.session_state._copilot_prefill = "What is the total amount of matched invoices?"
    with p3:
        if st.button("Settlement Cycle?", use_container_width=True):
            st.session_state._copilot_prefill = "What is the standard settlement cycle for merchants?"
    with p4:
        if st.button("Refund Policy?", use_container_width=True):
            st.session_state._copilot_prefill = "What is the refund processing policy?"

    st.write("")
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            if msg.get("route"):
                src_label = "Database (SQL)" if msg["route"] == "DATA" else "Policy Documents (RAG)"
                st.markdown(f'<span class="source-tag">Source: {src_label}</span>', unsafe_allow_html=True)
            if msg.get("is_safety", False) or msg["content"].startswith("[Security block]"):
                st.markdown(f'<div class="safety-block">{msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(msg["content"])

    prefill = st.session_state.pop("_copilot_prefill", None)
    user_input = st.chat_input("Ask about invoices or policies…")
    prompt_to_run = user_input or prefill

    if prompt_to_run:
        with st.chat_message("user"):
            st.markdown(prompt_to_run)
        st.session_state.chat_history.append({
            "role": "user",
            "content": prompt_to_run,
            "is_safety": False,
        })

        with st.chat_message("assistant"):
            with st.spinner("Formulating response..."):
                try:
                    result = route_and_answer(prompt_to_run)
                    answer = result.get("answer", "No answer formulated.")
                    route = result.get("route", "UNKNOWN")
                except Exception as e:
                    answer = f"Error processing query: {e}"
                    route = "ERROR"

            src_label = "Database (SQL)" if route == "DATA" else "Policy Documents (RAG)"
            st.markdown(f'<span class="source-tag">Source: {src_label}</span>', unsafe_allow_html=True)

            is_safety = answer.startswith("[Security block]")
            if is_safety:
                st.markdown(f'<div class="safety-block">{answer}</div>', unsafe_allow_html=True)
            else:
                st.markdown(answer)

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": answer,
            "route": route,
            "is_safety": is_safety,
        })

    if st.session_state.chat_history:
        st.write("")
        if st.button("Clear Conversation", use_container_width=False):
            st.session_state.chat_history = []
            st.rerun()


# ===========================================================================
# TAB 3: FULL PIPELINE
# ===========================================================================
with tab_pipeline:
    st.markdown("##### End-to-End Autonomous Pipeline")
    st.caption("Executes Data Loading ➔ Reconciliation ➔ Exception Diagnostics ➔ ML Forecasting ➔ Executive Synthesis.")

    run_pipeline_btn = st.button("Run LedgerMind Pipeline", type="primary", use_container_width=True)

    if run_pipeline_btn:
        with st.spinner("Executing LangGraph pipeline..."):
            inv_file = os.path.join(project_root, "data", "invoice.csv")
            bank_file = os.path.join(project_root, "data", "bank.csv")
            rev_file = os.path.join(project_root, "data", "revenue.csv")

            try:
                state = run_pipeline(inv_file, bank_file, rev_file)
                st.session_state.pipeline_result = state
                pdf_out = os.path.join(project_root, "reports", "ledgermind_report.pdf")
                generate_pdf_report(state, output_path=pdf_out)
            except Exception as e:
                st.error(f"Pipeline error: {e}")

    if st.session_state.pipeline_result is not None:
        p_res = st.session_state.pipeline_result
        report = p_res.get("final_report", {})
        forecast_df = p_res.get("forecast", pd.DataFrame())
        hist_df = p_res.get("historical_revenue", pd.DataFrame())
        matched_df = p_res.get("matched", pd.DataFrame())
        exceptions_df = p_res.get("exceptions", pd.DataFrame())

        st.write("")
        pdf_path = os.path.join(project_root, "reports", "ledgermind_report.pdf")
        if os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()
            st.download_button(
                label="Download Executive PDF Report",
                data=pdf_bytes,
                file_name="LedgerMind_Financial_Report.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

        st.write("")
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.metric("Total Invoices", report.get("total_invoices", 0))
        with k2:
            st.metric("Matched", report.get("matched_count", 0))
        with k3:
            st.metric("Exceptions", report.get("exception_count", 0))
        with k4:
            st.metric("Match Rate", f"{report.get('match_percentage', 0.0)}%")

        st.write("")
        c_chart, c_comm = st.columns([3, 2])

        with c_chart:
            st.markdown("##### Revenue Trajectory & Q3 Forecast")
            if not hist_df.empty and not forecast_df.empty:
                fig = go.Figure()

                # Historical line
                fig.add_trace(go.Scatter(
                    x=hist_df["month"],
                    y=hist_df["revenue"],
                    mode="lines+markers",
                    name="Historical",
                    line=dict(color="#4f46e5", width=2.5),
                    marker=dict(size=7, color="#4f46e5"),
                    hovertemplate="<b>%{x}</b>: $%{y:,.0f}<extra>Historical</extra>"
                ))

                # Projection bridge
                fig.add_trace(go.Scatter(
                    x=[hist_df["month"].iloc[-1], forecast_df["month"].iloc[0]],
                    y=[hist_df["revenue"].iloc[-1], forecast_df["predicted_revenue"].iloc[0]],
                    mode="lines",
                    name="Bridge",
                    line=dict(color="#818cf8", width=2, dash="dot"),
                    showlegend=False,
                    hoverinfo="skip"
                ))

                # Forecast line
                fig.add_trace(go.Scatter(
                    x=forecast_df["month"],
                    y=forecast_df["predicted_revenue"],
                    mode="lines+markers",
                    name="Q3 Forecast",
                    line=dict(color="#818cf8", width=2.5, dash="dash"),
                    marker=dict(size=8, symbol="diamond", color="#6366f1"),
                    hovertemplate="<b>%{x}</b>: $%{y:,.0f}<extra>Forecast</extra>"
                ))

                fig.update_layout(
                    paper_bgcolor="#ffffff",
                    plot_bgcolor="#ffffff",
                    margin=dict(l=20, r=20, t=25, b=20),
                    height=300,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    xaxis=dict(gridcolor="#f1f5f9", linecolor="#e2e8f0", title=None),
                    yaxis=dict(gridcolor="#f1f5f9", linecolor="#e2e8f0", title=None, tickprefix="$"),
                )
                st.plotly_chart(fig, use_container_width=True)

        with c_comm:
            st.markdown("##### Executive Strategic Commentary")
            summary_text = report.get("forecast_summary", "No commentary generated.")
            st.markdown(
                f"""
                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 1.1rem 1.3rem; font-size: 0.88rem; line-height: 1.6; color: #334155;">
                    <div style="color: #4f46e5; font-weight: 600; font-size: 0.78rem; text-transform: uppercase; margin-bottom: 0.4rem; letter-spacing: 0.04em;">
                        AI Strategic Synthesis
                    </div>
                    {summary_text}
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.write("")
        st.markdown("##### Pipeline Artifact Inspection")
        tab_m, tab_e, tab_f = st.tabs(["Matched", "Exceptions", "Forecast Data"])
        with tab_m:
            if not matched_df.empty:
                st.dataframe(matched_df, use_container_width=True, height=220)
            else:
                st.info("No matched records.")
        with tab_e:
            if not exceptions_df.empty:
                st.dataframe(exceptions_df, use_container_width=True, height=220)
            else:
                st.info("No exceptions.")
        with tab_f:
            if not forecast_df.empty:
                f_view = forecast_df.copy()
                f_view["predicted_revenue"] = f_view["predicted_revenue"].apply(lambda x: f"${x:,}")
                st.dataframe(f_view, use_container_width=True, height=220)

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown(
    '<div class="fintech-footer">LedgerMind AI &bull; Autonomous Financial Controller &bull; Built with LangGraph &amp; Gemini</div>',
    unsafe_allow_html=True,
)
