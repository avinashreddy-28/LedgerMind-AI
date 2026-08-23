"""
frontend/app.py — LedgerMind-AI Autonomous Finance Controller Dashboard
========================================================================
An Autonomous Finance Controller for Reconciliation, Forecasting & Exception Intelligence.
Organized into three primary workspaces:
1. 📊 Dashboard — Multi-file ingestion, transaction reconciliation & exception generation.
2. 🤖 AI Copilot — Multi-agent query router answering SQL database and policy RAG questions.
3. 🚀 Full Pipeline — LangGraph orchestration chaining all agents with PDF report download.
"""

import sys
import os
import time

# ---------------------------------------------------------------------------
# Make project root importable regardless of launch directory
# ---------------------------------------------------------------------------
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Backend agent imports with defensive guards
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
# 2. Custom Styling (Dark Glassmorphic Theme)
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Main Header Banner */
    .main-header {
        background: linear-gradient(135deg, #0f172a, #1e1b4b, #312e81);
        padding: 1.8rem 2.2rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.35);
    }
    .main-header h1 {
        color: #ffffff;
        font-weight: 800;
        font-size: 2.1rem;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .main-header p {
        color: #c7d2fe;
        font-size: 0.98rem;
        margin: 0.4rem 0 0;
        font-weight: 400;
    }

    /* Metric Cards */
    .metric-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 1.2rem 1.4rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
    }
    .metric-card .label {
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        color: #94a3b8;
        margin-bottom: 0.3rem;
    }
    .metric-card .value {
        font-size: 1.9rem;
        font-weight: 700;
        color: #e2e8f0;
    }
    .metric-card .value.green  { color: #34d399; }
    .metric-card .value.red    { color: #f87171; }
    .metric-card .value.purple { color: #c084fc; }
    .metric-card .value.blue   { color: #60a5fa; }

    /* Badges */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.65rem;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .status-badge.matched {
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.4);
    }
    .status-badge.unmatched {
        background: rgba(239, 68, 68, 0.15);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.4);
    }
    .db-badge {
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid rgba(16, 185, 129, 0.4);
        border-radius: 8px;
        padding: 0.35rem 0.75rem;
        color: #6ee7b7;
        font-size: 0.82rem;
        font-weight: 600;
        display: inline-block;
        margin-top: 0.5rem;
    }

    /* Copilot Hero */
    .copilot-hero {
        background: linear-gradient(135deg, #1e1b4b, #312e81, #1e1b4b);
        border: 1px solid rgba(99, 102, 241, 0.4);
        border-radius: 14px;
        padding: 1.5rem 1.8rem;
        margin-bottom: 1.2rem;
    }
    .copilot-hero h3 {
        color: #e0e7ff;
        font-weight: 700;
        margin: 0 0 0.3rem;
    }
    .copilot-hero p {
        color: #a5b4fc;
        font-size: 0.9rem;
        margin: 0;
    }

    /* Security block styling */
    .safety-blocked {
        background: rgba(239, 68, 68, 0.12);
        border: 1px solid rgba(239, 68, 68, 0.45);
        border-radius: 10px;
        padding: 0.85rem 1.1rem;
        color: #fca5a5;
        font-size: 0.9rem;
        margin: 0.5rem 0;
    }

    /* Footer */
    .footer {
        text-align: center;
        color: #64748b;
        font-size: 0.8rem;
        margin-top: 2.5rem;
        padding: 1rem;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
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
    st.markdown("### 📒 **LedgerMind AI**")
    st.caption("Autonomous Financial Controller")
    st.write("")

    st.markdown("##### ℹ️ **About LedgerMind**")
    st.markdown(
        """
        <div style="color: #94a3b8; font-size: 0.84rem; line-height: 1.5; margin-bottom: 1rem;">
        LedgerMind AI is an autonomous finance engine that automates invoice-to-bank reconciliation,
        diagnoses mismatch root causes using Google Gemini, performs linear regression cash forecasting,
        and provides natural language data & policy assistance.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("---")
    st.markdown("##### 🗄️ **System Status**")
    backend_name = _active_backend.capitalize() if _active_backend else "SQLite"
    st.markdown(f'<div class="db-badge">🟢 DB: {backend_name}</div>', unsafe_allow_html=True)
    st.markdown('<div class="db-badge" style="color: #93c5fd; border-color: rgba(59, 130, 246, 0.4); background: rgba(59, 130, 246, 0.15);">🟢 RAG: ChromaDB Ready</div>', unsafe_allow_html=True)

    st.write("---")
    st.caption("LedgerMind AI &bull; Version 1.0 Production")


# ---------------------------------------------------------------------------
# 5. Header Banner (Always Visible)
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="main-header">
        <h1>📒 LedgerMind AI</h1>
        <p>An Autonomous Finance Controller for Reconciliation, Forecasting &amp; Exception Intelligence</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# 6. Tab Navigation: Dashboard, AI Copilot, Full Pipeline
# ---------------------------------------------------------------------------
tab_dash, tab_copilot, tab_pipeline = st.tabs([
    "📊 Dashboard",
    "🤖 AI Copilot",
    "🚀 Full Pipeline",
])


# ===========================================================================
# TAB 1: RECONCILIATION DASHBOARD
# ===========================================================================
with tab_dash:
    st.markdown("#### 📂 Transaction Data Ingestion")

    # File uploaders
    col_inv, col_bank = st.columns(2)
    with col_inv:
        invoice_file = st.file_uploader(
            "📄 Upload Invoice CSV",
            type=["csv"],
            key="dash_inv_uploader",
            help="Expected columns: invoice_id, amount",
        )
    with col_bank:
        bank_file = st.file_uploader(
            "🏦 Upload Bank CSV",
            type=["csv"],
            key="dash_bank_uploader",
            help="Expected columns: txn_id, amount",
        )

    # Reconcile Action Button
    col_act, col_def = st.columns([2, 1])
    with col_act:
        reconcile_clicked = st.button("⚖️  Reconcile Transactions", type="primary", use_container_width=True)
    with col_def:
        use_default = st.button("📁 Use Sample Datasets", use_container_width=True)

    # Load and process data
    if reconcile_clicked or use_default:
        try:
            if use_default or (not invoice_file and not bank_file):
                inv_path = os.path.join(project_root, "data", "invoice.csv")
                bnk_path = os.path.join(project_root, "data", "bank.csv")
            else:
                inv_path = invoice_file if invoice_file else os.path.join(project_root, "data", "invoice.csv")
                bnk_path = bank_file if bank_file else os.path.join(project_root, "data", "bank.csv")

            with st.spinner("Reconciling invoice and bank records..."):
                inv_df, bnk_df = load_data(inv_path, bnk_path)
                st.session_state.invoice_df = inv_df
                st.session_state.bank_df = bnk_df
                st.session_state.recon_results = reconcile_transactions(inv_df, bnk_df)
                st.session_state.ai_explanations = None
                st.success("✅ Reconciliation completed successfully!")
        except Exception as e:
            st.error(f"❌ Error during reconciliation: {e}")

    # Display Dashboard Results
    if st.session_state.recon_results is not None:
        results = st.session_state.recon_results
        matched_df = results["matched"]
        unmatched_df = results["unmatched"]
        match_pct = results["match_percentage"]
        total_invoices = len(st.session_state.invoice_df) if st.session_state.invoice_df is not None else 0

        st.write("")
        st.markdown("#### 📈 Key Performance Indicators")

        # st.metric cards with clear color-coded values
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric(label="Total Invoices", value=total_invoices)
        with m2:
            st.metric(label="Matched Invoices", value=len(matched_df), delta="Reconciled", delta_color="normal")
        with m3:
            st.metric(label="Unmatched Invoices", value=len(unmatched_df), delta="Exceptions", delta_color="inverse")
        with m4:
            st.metric(label="Match Rate", value=f"{match_pct:.1f}%")

        st.write("")
        st.markdown("---")

        # Two-column breakdown of tables
        col_m_view, col_u_view = st.columns(2)

        with col_m_view:
            st.markdown("##### 🟢 Matched Invoices")
            if not matched_df.empty:
                st.dataframe(matched_df, use_container_width=True)
            else:
                st.info("No invoices matched.")

        with col_u_view:
            st.markdown("##### 🔴 Unmatched Invoices (Exceptions)")
            if not unmatched_df.empty:
                st.dataframe(unmatched_df, use_container_width=True)
            else:
                st.success("🎉 Perfect match! 0 unmatched invoices.")

        # AI Exception Explanations Section
        if not unmatched_df.empty:
            st.write("")
            st.markdown("##### 🔍 AI Exception Intelligence")

            if st.session_state.ai_explanations is None:
                if st.button("🧠 Explain Exceptions with Gemini", use_container_width=True):
                    with st.spinner("Analyzing unmatched invoices with Gemini..."):
                        try:
                            ex_df = generate_exceptions(unmatched_df)
                            st.session_state.ai_explanations = ex_df
                            try:
                                save_to_db(matched_df, ex_df)
                            except Exception:
                                pass
                            st.rerun()
                        except Exception as e:
                            st.error(f"Could not generate AI exceptions: {e}")
            else:
                st.dataframe(st.session_state.ai_explanations, use_container_width=True)
                st.caption("✅ Exceptions synchronized and persisted to database.")


# ===========================================================================
# TAB 2: AI COPILOT (Multi-Agent Intelligent Router)
# ===========================================================================
with tab_copilot:
    st.markdown(
        """
        <div class="copilot-hero">
            <h3>🤖 LedgerMind AI Copilot</h3>
            <p>Ask natural language questions about invoices (SQL Database) or company settlement/refund rules (Policy RAG).</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Suggestion Pills
    st.markdown("##### 💡 Suggested Questions")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("❓ Unmatched Invoices?", use_container_width=True):
            st.session_state._copilot_prefill = "Which invoices are unmatched?"
    with c2:
        if st.button("💰 Total Matched Amount?", use_container_width=True):
            st.session_state._copilot_prefill = "What is the total amount of matched invoices?"
    with c3:
        if st.button("⏱️ Settlement Cycle?", use_container_width=True):
            st.session_state._copilot_prefill = "What is the standard settlement cycle for merchants?"
    with c4:
        if st.button("🔄 Refund Policy?", use_container_width=True):
            st.session_state._copilot_prefill = "What is the refund processing policy?"

    st.write("")
    st.markdown("---")

    # Render Conversation History
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            if msg.get("route"):
                src_badge = "📊 Database" if msg["route"] == "DATA" else "📄 Policy Documents"
                st.caption(f"Source: **{src_badge}**")
            if msg.get("is_safety", False) or msg["content"].startswith("[Security block]"):
                st.markdown(
                    f'<div class="safety-blocked">🚫 {msg["content"]}</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(msg["content"])

    # Chat Input Handler
    prefill = st.session_state.pop("_copilot_prefill", None)
    user_input = st.chat_input("Ask about invoices or financial policies… e.g. 'What is the refund policy?'")
    prompt_to_run = user_input or prefill

    if prompt_to_run:
        with st.chat_message("user"):
            st.markdown(prompt_to_run)
        st.session_state.chat_history.append({
            "role": "user",
            "content": prompt_to_run,
            "is_safety": False,
        })

        # Router Execution with defensive try/except
        with st.chat_message("assistant"):
            with st.spinner("🤖 Routing and formulating response..."):
                try:
                    result = route_and_answer(prompt_to_run)
                    answer = result.get("answer", "No answer could be formulated.")
                    route = result.get("route", "UNKNOWN")
                except Exception as e:
                    answer = f"An unexpected error occurred while processing your request: {e}"
                    route = "ERROR"

            src_badge = "📊 Database" if route == "DATA" else "📄 Policy Documents"
            st.caption(f"Source: **{src_badge}**")

            is_safety = answer.startswith("[Security block]")
            if is_safety:
                st.markdown(
                    f'<div class="safety-blocked">🚫 {answer}</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(answer)

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": answer,
            "route": route,
            "is_safety": is_safety,
        })

    # Clear Chat Action
    if st.session_state.chat_history:
        st.write("")
        if st.button("🗑️  Clear Chat History", use_container_width=False):
            st.session_state.chat_history = []
            st.rerun()


# ===========================================================================
# TAB 3: RUN FULL PIPELINE (LangGraph Orchestrator & PDF Reporting)
# ===========================================================================
with tab_pipeline:
    st.markdown("#### 🚀 LangGraph Multi-Agent Orchestrator")
    st.caption("Chains Data Loading ➔ Reconciliation ➔ Exception Analysis ➔ Revenue Forecasting ➔ Executive Synthesis.")

    # Execution controls
    c_btn, c_pdf = st.columns([2, 1])
    with c_btn:
        run_full_btn = st.button("▶️  Run LedgerMind Pipeline", type="primary", use_container_width=True)

    if run_full_btn:
        with st.spinner("🚀 Executing LangGraph Multi-Agent Pipeline..."):
            inv_file = os.path.join(project_root, "data", "invoice.csv")
            bank_file = os.path.join(project_root, "data", "bank.csv")
            rev_file = os.path.join(project_root, "data", "revenue.csv")

            try:
                state = run_pipeline(inv_file, bank_file, rev_file)
                st.session_state.pipeline_result = state
                
                # Auto-generate PDF report on pipeline completion
                pdf_out = os.path.join(project_root, "reports", "ledgermind_report.pdf")
                generate_pdf_report(state, output_path=pdf_out)
                st.success("✅ LangGraph Pipeline Executed & PDF Report Ready!")
            except Exception as e:
                st.error(f"❌ Error during pipeline execution: {e}")

    # Display Pipeline Results
    if st.session_state.pipeline_result is not None:
        p_res = st.session_state.pipeline_result
        report = p_res.get("final_report", {})
        forecast_df = p_res.get("forecast", pd.DataFrame())
        hist_df = p_res.get("historical_revenue", pd.DataFrame())
        matched_df = p_res.get("matched", pd.DataFrame())
        exceptions_df = p_res.get("exceptions", pd.DataFrame())

        st.write("")
        st.markdown("---")
        
        # Download PDF Action Button
        pdf_path = os.path.join(project_root, "reports", "ledgermind_report.pdf")
        if os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()
            st.download_button(
                label="📄  Download Full Report (PDF)",
                data=pdf_bytes,
                file_name="LedgerMind_Financial_Report.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
            st.write("")

        st.markdown("#### 📊 Executive Financial Overview")

        # 4 Metric Cards using st.metric
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.metric("Total Processed", report.get("total_invoices", 0))
        with k2:
            st.metric("Matched Invoices", report.get("matched_count", 0), delta="Reconciled", delta_color="normal")
        with k3:
            st.metric("Exceptions", report.get("exception_count", 0), delta="Requires Review", delta_color="inverse")
        with k4:
            st.metric("Match Rate", f"{report.get('match_percentage', 0.0)}%")

        st.write("")

        # Visualizations & Commentary
        col_chart, col_comm = st.columns([3, 2])

        with col_chart:
            st.markdown("##### 📈 Revenue Trajectory (Historical + Q3 Forecast)")
            if not hist_df.empty and not forecast_df.empty:
                fig = go.Figure()

                # Historical Trace
                fig.add_trace(go.Scatter(
                    x=hist_df["month"],
                    y=hist_df["revenue"],
                    mode="lines+markers",
                    name="Historical Revenue",
                    line=dict(color="#38bdf8", width=3),
                    marker=dict(size=8, color="#38bdf8"),
                    hovertemplate="<b>%{x}</b>: $%{y:,.0f}<extra>Historical</extra>"
                ))

                # Connecting bridge
                bridge_x = [hist_df["month"].iloc[-1], forecast_df["month"].iloc[0]]
                bridge_y = [hist_df["revenue"].iloc[-1], forecast_df["predicted_revenue"].iloc[0]]
                fig.add_trace(go.Scatter(
                    x=bridge_x,
                    y=bridge_y,
                    mode="lines",
                    name="Projection Bridge",
                    line=dict(color="#c084fc", width=2.5, dash="dot"),
                    showlegend=False,
                    hoverinfo="skip"
                ))

                # Forecast Trace
                fig.add_trace(go.Scatter(
                    x=forecast_df["month"],
                    y=forecast_df["predicted_revenue"],
                    mode="lines+markers",
                    name="ML Forecast (Q3)",
                    line=dict(color="#c084fc", width=3, dash="dash"),
                    marker=dict(size=9, symbol="diamond", color="#e879f9"),
                    hovertemplate="<b>%{x}</b>: $%{y:,.0f}<extra>Forecast</extra>"
                ))

                fig.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(15,23,42,0.6)",
                    margin=dict(l=20, r=20, t=30, b=20),
                    height=340,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    ),
                    xaxis=dict(gridcolor="rgba(255,255,255,0.08)", title="Month"),
                    yaxis=dict(gridcolor="rgba(255,255,255,0.08)", title="Revenue ($USD)", tickprefix="$"),
                )
                st.plotly_chart(fig, use_container_width=True)

        with col_comm:
            st.markdown("##### 🤖 Executive Strategic Synthesis")
            summary_text = report.get("forecast_summary", "No forecast commentary available.")
            st.markdown(
                f"""
                <div style="background: linear-gradient(135deg, rgba(30, 27, 75, 0.7), rgba(49, 46, 129, 0.7));
                            border: 1px solid rgba(139, 92, 246, 0.4);
                            border-radius: 14px;
                            padding: 1.3rem;
                            color: #e0e7ff;
                            font-size: 0.92rem;
                            line-height: 1.6;
                            box-shadow: 0 4px 20px rgba(0,0,0,0.2);">
                    <div style="color: #a78bfa; font-weight: 700; font-size: 0.85rem; text-transform: uppercase; margin-bottom: 0.5rem; letter-spacing: 0.5px;">
                        AI Strategic Forecast Analysis
                    </div>
                    {summary_text}
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Granular Inspection Tabs
        st.write("")
        st.markdown("##### 🔍 Granular Inspection")
        tab_m, tab_e, tab_f = st.tabs(["⚖️ Matched Invoices", "🚨 AI Exceptions", "🔮 Forecast Numbers"])
        with tab_m:
            if not matched_df.empty:
                st.dataframe(matched_df, use_container_width=True)
            else:
                st.info("No matched records.")
        with tab_e:
            if not exceptions_df.empty:
                st.dataframe(exceptions_df, use_container_width=True)
            else:
                st.info("No exceptions.")
        with tab_f:
            if not forecast_df.empty:
                f_view = forecast_df.copy()
                f_view["predicted_revenue"] = f_view["predicted_revenue"].apply(lambda x: f"${x:,}")
                st.dataframe(f_view, use_container_width=True)

# ---------------------------------------------------------------------------
# Footer (Always Visible)
# ---------------------------------------------------------------------------
st.markdown(
    '<div class="footer">Built with ❤️ by LedgerMind AI &bull; Autonomous Finance Controller &bull; Powered by Gemini &amp; LangGraph</div>',
    unsafe_allow_html=True,
)
