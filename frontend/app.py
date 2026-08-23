"""
frontend/app.py — LedgerMind AI Autonomous Finance Controller Dashboard
========================================================================
A high-performance, technical "AI Dev-Tool" interface for transaction reconciliation,
ChromaDB policy RAG, Text-to-SQL Copilot, and LangGraph cash forecasting.
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
    page_title="LedgerMind AI // Controller",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize database backend safely
try:
    init_db()
except Exception:
    pass

# ---------------------------------------------------------------------------
# 2. Modern Technical "Dev-Tool" CSS Design System
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    /* ---------- Chrome & Clutter Removal ---------- */
    #MainMenu, footer, header {
        visibility: hidden !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    html, body, [class*="css"], .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        background-color: #FAFAFA !important;
        color: #1A1A1A !important;
        letter-spacing: -0.015em;
    }

    code, pre, .terminal-text {
        font-family: 'JetBrains Mono', monospace !important;
    }

    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2.5rem !important;
        max-width: 1240px !important;
    }

    /* ---------- Top App Bar / Dev-Tool Header ---------- */
    .dev-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 1.15rem 1.6rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    }
    .dev-header-left {
        display: flex;
        align-items: center;
        gap: 0.9rem;
    }
    .dev-logo-badge {
        background: #FFF7ED;
        border: 1px solid #FFEDD5;
        color: #FF6B1A;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 800;
        font-size: 1.1rem;
        width: 38px;
        height: 38px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 8px;
    }
    .dev-header-titles h1 {
        font-size: 1.35rem;
        font-weight: 800;
        color: #111827;
        margin: 0;
        letter-spacing: -0.03em;
        line-height: 1.2;
    }
    .dev-header-titles p {
        font-size: 0.82rem;
        color: #6B7280;
        margin: 0.15rem 0 0 0;
        font-family: 'JetBrains Mono', monospace;
    }
    .dev-status-pill {
        display: flex;
        align-items: center;
        gap: 0.45rem;
        background: #111827;
        color: #F9FAFB;
        border-radius: 6px;
        padding: 0.35rem 0.75rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .pulse-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background-color: #FF6B1A;
        box-shadow: 0 0 8px rgba(255, 107, 26, 0.8);
    }

    /* ---------- Icon-Badge Metric Cards ---------- */
    .metric-card-dev {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 1.1rem 1.25rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        height: 100%;
    }
    .metric-card-dev:hover {
        border-color: #D1D5DB;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        transform: translateY(-1px);
    }
    .metric-top-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }
    .metric-icon-badge {
        width: 32px;
        height: 32px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.95rem;
    }
    .metric-icon-orange { background: #FFF7ED; color: #EA580C; border: 1px solid #FFEDD5; }
    .metric-icon-blue   { background: #EFF6FF; color: #2563EB; border: 1px solid #DBEAFE; }
    .metric-icon-red    { background: #FEF2F2; color: #DC2626; border: 1px solid #FEE2E2; }
    .metric-icon-green  { background: #F0FDF4; color: #16A34A; border: 1px solid #DCFCE7; }
    
    .metric-tag {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        font-weight: 600;
        color: #6B7280;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    .metric-main-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.75rem;
        font-weight: 700;
        color: #111827;
        letter-spacing: -0.03em;
        margin: 0.2rem 0;
    }
    .metric-sub-label {
        font-size: 0.76rem;
        color: #6B7280;
    }

    /* ---------- Terminal Output Cards ---------- */
    .terminal-card {
        background: #0D0E15;
        border: 1px solid #1E293B;
        border-radius: 12px;
        padding: 0;
        overflow: hidden;
        margin: 0.85rem 0;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
        font-family: 'JetBrains Mono', monospace;
    }
    .terminal-topbar {
        background: #161822;
        padding: 0.55rem 1rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #232738;
    }
    .terminal-dots {
        display: flex;
        gap: 6px;
    }
    .dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
    }
    .dot-red    { background: #EF4444; }
    .dot-yellow { background: #F59E0B; }
    .dot-green  { background: #10B981; }
    .terminal-title {
        font-size: 0.75rem;
        color: #94A3B8;
        font-weight: 600;
    }
    .terminal-body {
        padding: 1.1rem 1.25rem;
        color: #E2E8F0;
        font-size: 0.88rem;
        line-height: 1.6;
    }
    .terminal-prompt {
        color: #FF6B1A;
        font-weight: 700;
        margin-right: 0.4rem;
    }
    .terminal-highlight {
        color: #38BDF8;
        font-weight: 600;
    }
    .terminal-success {
        color: #34D399;
    }
    .terminal-warn {
        color: #F87171;
    }
    .terminal-dim {
        color: #64748B;
    }

    /* ---------- Sidebar Technical Styling ---------- */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E5E7EB !important;
    }
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: #111827 !important;
        font-size: 1.1rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.02em !important;
    }
    .sidebar-sys-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 0.85rem;
        margin-top: 0.75rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.76rem;
    }
    .sidebar-sys-row {
        display: flex;
        justify-content: space-between;
        padding: 0.25rem 0;
        color: #475569;
    }
    .sidebar-sys-row span.active {
        color: #FF6B1A;
        font-weight: 700;
    }

    /* ---------- Buttons & CTAs ---------- */
    .stButton > button {
        border-radius: 8px !important;
        padding: 0.55rem 1.2rem !important;
        font-weight: 600 !important;
        font-size: 0.86rem !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        border: 1px solid #E5E7EB !important;
        background-color: #FFFFFF !important;
        color: #1F2937 !important;
    }
    .stButton > button:hover {
        border-color: #CBD5E1 !important;
        background-color: #F8FAFC !important;
        color: #111827 !important;
    }
    .stButton > button[kind="primary"] {
        background-color: #FF6B1A !important;
        color: #FFFFFF !important;
        border: none !important;
        box-shadow: 0 1px 3px rgba(255, 107, 26, 0.3) !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #EA580C !important;
        box-shadow: 0 4px 14px rgba(255, 107, 26, 0.4) !important;
        transform: translateY(-1px);
    }

    /* ---------- Tabs Navigation ---------- */
    [data-testid="stTabs"] {
        margin-bottom: 1.25rem !important;
    }
    [data-testid="stTabs"] button {
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        color: #6B7280 !important;
        padding: 0.65rem 1.25rem !important;
        border-radius: 6px 6px 0 0 !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stTabs"] button[aria-selected="true"] {
        color: #FF6B1A !important;
        font-weight: 700 !important;
        border-bottom: 2px solid #FF6B1A !important;
    }

    /* ---------- Chat Message Cards ---------- */
    [data-testid="stChatMessage"] {
        background: #FFFFFF !important;
        border: 1px solid #E5E7EB !important;
        border-radius: 10px !important;
        padding: 0.85rem 1.15rem !important;
        margin-bottom: 0.65rem !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02) !important;
    }

    .source-badge {
        display: inline-block;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        font-weight: 700;
        padding: 0.2rem 0.55rem;
        border-radius: 4px;
        margin-bottom: 0.45rem;
    }
    .source-badge.db {
        background: #EFF6FF;
        color: #2563EB;
        border: 1px solid #DBEAFE;
    }
    .source-badge.rag {
        background: #FFF7ED;
        color: #EA580C;
        border: 1px solid #FFEDD5;
    }

    /* ---------- DataFrames ---------- */
    .stDataFrame {
        border-radius: 10px !important;
        overflow: hidden !important;
        border: 1px solid #E5E7EB !important;
    }

    /* ---------- Footer ---------- */
    .dev-footer {
        text-align: center;
        color: #9CA3AF;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        margin-top: 3rem;
        padding: 1rem 0;
        border-top: 1px solid #E5E7EB;
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
# 4. Sidebar Technical Panel
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚡ **LedgerMind**")
    st.caption("Autonomous Financial Controller")
    st.write("")

    st.markdown("##### **Architecture**")
    st.markdown(
        """
        <div style="color: #4B5563; font-size: 0.83rem; line-height: 1.5; margin-bottom: 0.75rem;">
        Multi-agent financial engine orchestrating deterministic reconciliation, 
        ChromaDB policy retrieval, text-to-SQL query generation, and predictive cash flow modeling.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("##### **Runtime Environment**")
    backend_label = _active_backend.capitalize() if _active_backend else "SQLite"
    st.markdown(
        f"""
        <div class="sidebar-sys-card">
            <div class="sidebar-sys-row"><span>Engine:</span> <span class="active">LangGraph 0.2</span></div>
            <div class="sidebar-sys-row"><span>Database:</span> <span class="active">{backend_label}</span></div>
            <div class="sidebar-sys-row"><span>Vector Store:</span> <span class="active">ChromaDB</span></div>
            <div class="sidebar-sys-row"><span>Foundation Model:</span> <span class="active">Gemini 3.7</span></div>
            <div class="sidebar-sys-row"><span>Status:</span> <span style="color: #10B981; font-weight:700;">LIVE</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("---")
    st.caption("LedgerMind AI &bull; Version 1.0 Production")


# ---------------------------------------------------------------------------
# 5. Top Dev-Tool App Header
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="dev-header">
        <div class="dev-header-left">
            <div class="dev-logo-badge">LM</div>
            <div class="dev-header-titles">
                <h1>LedgerMind AI</h1>
                <p>AUTONOMOUS FINANCE ENGINE // RECONCILIATION &amp; REVENUE FORECASTING</p>
            </div>
        </div>
        <div class="dev-status-pill">
            <span class="pulse-dot"></span>
            AGENT CLUSTER: ACTIVE
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# 6. Tab Navigation: Dashboard, AI Copilot, Full Pipeline
# ---------------------------------------------------------------------------
tab_dash, tab_copilot, tab_pipeline = st.tabs([
    "⚡ Reconciliation Engine",
    "🤖 Multi-Agent Copilot",
    "🚀 LangGraph Pipeline",
])


# ===========================================================================
# TAB 1: RECONCILIATION DASHBOARD
# ===========================================================================
with tab_dash:
    st.markdown("##### **Data Ingestion & Deterministic Matching**")

    # File uploaders
    col_inv, col_bank = st.columns(2)
    with col_inv:
        invoice_file = st.file_uploader(
            "Invoice Register (CSV)",
            type=["csv"],
            key="dash_inv_uploader",
        )
    with col_bank:
        bank_file = st.file_uploader(
            "Bank Statement Stream (CSV)",
            type=["csv"],
            key="dash_bank_uploader",
        )

    # Action Controls
    c_rec, c_smp = st.columns([2, 1])
    with c_rec:
        reconcile_clicked = st.button("Execute Transaction Matcher", type="primary", use_container_width=True)
    with c_smp:
        use_default = st.button("Load Standard Sample (50 txns)", use_container_width=True)

    # Ingestion & Reconciliation Logic
    if reconcile_clicked or use_default:
        try:
            if use_default or (not invoice_file and not bank_file):
                inv_path = os.path.join(project_root, "data", "invoice.csv")
                bnk_path = os.path.join(project_root, "data", "bank.csv")
            else:
                inv_path = invoice_file if invoice_file else os.path.join(project_root, "data", "invoice.csv")
                bnk_path = bank_file if bank_file else os.path.join(project_root, "data", "bank.csv")

            with st.spinner("Ingesting and matching transactional streams..."):
                inv_df, bnk_df = load_data(inv_path, bnk_path)
                st.session_state.invoice_df = inv_df
                st.session_state.bank_df = bnk_df
                st.session_state.recon_results = reconcile_transactions(inv_df, bnk_df)
                st.session_state.ai_explanations = None
        except Exception as e:
            st.error(f"Reconciliation failure: {e}")

    # Render Reconciliation Results
    if st.session_state.recon_results is not None:
        results = st.session_state.recon_results
        matched_df = results["matched"]
        unmatched_df = results["unmatched"]
        match_pct = results["match_percentage"]
        total_inv = len(st.session_state.invoice_df) if st.session_state.invoice_df is not None else 0

        st.write("")
        # 4 Icon-Badge Metric Cards in a balanced grid
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(
                f"""
                <div class="metric-card-dev">
                    <div class="metric-top-row">
                        <span class="metric-tag">TOTAL PROCESSED</span>
                        <div class="metric-icon-badge metric-icon-blue">📊</div>
                    </div>
                    <div class="metric-main-value">{total_inv}</div>
                    <div class="metric-sub-label">Ingested invoice lines</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with m2:
            st.markdown(
                f"""
                <div class="metric-card-dev">
                    <div class="metric-top-row">
                        <span class="metric-tag">MATCHED</span>
                        <div class="metric-icon-badge metric-icon-green">✓</div>
                    </div>
                    <div class="metric-main-value">{len(matched_df)}</div>
                    <div class="metric-sub-label">Deterministic settlement</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with m3:
            st.markdown(
                f"""
                <div class="metric-card-dev">
                    <div class="metric-top-row">
                        <span class="metric-tag">EXCEPTIONS</span>
                        <div class="metric-icon-badge metric-icon-red">⚠</div>
                    </div>
                    <div class="metric-main-value" style="color: #DC2626;">{len(unmatched_df)}</div>
                    <div class="metric-sub-label">Requires AI diagnosis</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with m4:
            st.markdown(
                f"""
                <div class="metric-card-dev">
                    <div class="metric-top-row">
                        <span class="metric-tag">MATCH RATE</span>
                        <div class="metric-icon-badge metric-icon-orange">⚡</div>
                    </div>
                    <div class="metric-main-value" style="color: #FF6B1A;">{match_pct:.1f}%</div>
                    <div class="metric-sub-label">Automated close ratio</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.write("")
        # Data inspection grids
        c_m, c_u = st.columns(2)
        with c_m:
            st.markdown("##### **Matched Invoices**")
            if not matched_df.empty:
                st.dataframe(matched_df, use_container_width=True, height=280)
            else:
                st.info("No matching records found.")

        with c_u:
            st.markdown("##### **Unmatched Invoices (Exceptions)**")
            if not unmatched_df.empty:
                st.dataframe(unmatched_df, use_container_width=True, height=280)
            else:
                st.success("Zero exceptions. Clean reconciliation ledger.")

        # AI Exception Explanations Section
        if not unmatched_df.empty:
            st.write("")
            st.markdown("##### **AI Exception Root-Cause Intelligence**")
            if st.session_state.ai_explanations is None:
                if st.button("Diagnose Exceptions with Gemini", use_container_width=True):
                    with st.spinner("Executing Exception Agent root-cause diagnosis..."):
                        try:
                            ex_df = generate_exceptions(unmatched_df)
                            st.session_state.ai_explanations = ex_df
                            try:
                                save_to_db(matched_df, ex_df)
                            except Exception:
                                pass
                            st.rerun()
                        except Exception as e:
                            st.error(f"Exception analysis failure: {e}")
            else:
                st.dataframe(st.session_state.ai_explanations, use_container_width=True)


# ===========================================================================
# TAB 2: MULTI-AGENT COPILOT (Router / SQL / Policy RAG)
# ===========================================================================
with tab_copilot:
    st.markdown("##### **Natural Language Query Interface**")
    st.caption("Dispatches SQL queries against the ledger database or ChromaDB semantic policy documents.")

    # Technical Query Presets
    p1, p2, p3, p4 = st.columns(4)
    with p1:
        if st.button("Unmatched Invoices", use_container_width=True):
            st.session_state._copilot_prefill = "Which invoices are unmatched?"
    with p2:
        if st.button("Total Matched Sum", use_container_width=True):
            st.session_state._copilot_prefill = "What is the total amount of matched invoices?"
    with p3:
        if st.button("Settlement SLA", use_container_width=True):
            st.session_state._copilot_prefill = "What is the standard settlement cycle for merchants?"
    with p4:
        if st.button("Escalation SLA", use_container_width=True):
            st.session_state._copilot_prefill = "What happens to transactions unmatched for more than 7 days?"

    st.write("")
    # Render Conversation History with Terminal Styling
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            if msg["role"] == "assistant":
                route = msg.get("route", "UNKNOWN")
                badge_class = "db" if route == "DATA" else "rag"
                badge_text = "ROUTE: DATABASE (TEXT-TO-SQL)" if route == "DATA" else "ROUTE: POLICY (CHROMADB RAG)"
                st.markdown(f'<span class="source-badge {badge_class}">[ {badge_text} ]</span>', unsafe_allow_html=True)
                
                is_safety = msg.get("is_safety", False) or msg["content"].startswith("[Security block]")
                status_dot_class = "dot-red" if is_safety else "dot-green"
                
                st.markdown(
                    f"""
                    <div class="terminal-card">
                        <div class="terminal-topbar">
                            <div class="terminal-dots">
                                <span class="dot {status_dot_class}"></span>
                                <span class="dot dot-yellow"></span>
                                <span class="dot dot-green"></span>
                            </div>
                            <span class="terminal-title">ledgermind:agent-response // {route}</span>
                        </div>
                        <div class="terminal-body">
                            {msg["content"]}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(msg["content"])

    # Chat Input Handler
    prefill = st.session_state.pop("_copilot_prefill", None)
    user_input = st.chat_input("Query ledger database or company policies…")
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
            with st.spinner("Routing query and executing agent graph..."):
                try:
                    result = route_and_answer(prompt_to_run)
                    answer = result.get("answer", "No answer could be formulated.")
                    route = result.get("route", "UNKNOWN")
                except Exception as e:
                    answer = f"Agent execution error: {e}"
                    route = "ERROR"

            badge_class = "db" if route == "DATA" else "rag"
            badge_text = "ROUTE: DATABASE (TEXT-TO-SQL)" if route == "DATA" else "ROUTE: POLICY (CHROMADB RAG)"
            st.markdown(f'<span class="source-badge {badge_class}">[ {badge_text} ]</span>', unsafe_allow_html=True)

            is_safety = answer.startswith("[Security block]")
            status_dot_class = "dot-red" if is_safety else "dot-green"

            st.markdown(
                f"""
                <div class="terminal-card">
                    <div class="terminal-topbar">
                        <div class="terminal-dots">
                            <span class="dot {status_dot_class}"></span>
                            <span class="dot dot-yellow"></span>
                            <span class="dot dot-green"></span>
                        </div>
                        <span class="terminal-title">ledgermind:agent-response // {route}</span>
                    </div>
                    <div class="terminal-body">
                        {answer}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": answer,
            "route": route,
            "is_safety": is_safety,
        })

    if st.session_state.chat_history:
        st.write("")
        if st.button("Clear Terminal Log", use_container_width=False):
            st.session_state.chat_history = []
            st.rerun()


# ===========================================================================
# TAB 3: LANGGRAPH PIPELINE & EXECUTIVE REPORTING
# ===========================================================================
with tab_pipeline:
    st.markdown("##### **LangGraph Multi-Agent Pipeline Orchestration**")
    st.caption("Executes stateful pipeline: Ingestion ➔ Matching ➔ Exception Diagnosis ➔ Scikit-Learn Forecast ➔ PDF Report.")

    run_pipeline_btn = st.button("Execute Pipeline Graph", type="primary", use_container_width=True)

    if run_pipeline_btn:
        with st.spinner("Orchestrating 5-node LangGraph pipeline..."):
            inv_file = os.path.join(project_root, "data", "invoice.csv")
            bank_file = os.path.join(project_root, "data", "bank.csv")
            rev_file = os.path.join(project_root, "data", "revenue.csv")

            try:
                state = run_pipeline(inv_file, bank_file, rev_file)
                st.session_state.pipeline_result = state
                pdf_out = os.path.join(project_root, "reports", "ledgermind_report.pdf")
                generate_pdf_report(state, output_path=pdf_out)
            except Exception as e:
                st.error(f"Pipeline orchestration error: {e}")

    if st.session_state.pipeline_result is not None:
        p_res = st.session_state.pipeline_result
        report = p_res.get("final_report", {})
        forecast_df = p_res.get("forecast", pd.DataFrame())
        hist_df = p_res.get("historical_revenue", pd.DataFrame())
        matched_df = p_res.get("matched", pd.DataFrame())
        exceptions_df = p_res.get("exceptions", pd.DataFrame())

        st.write("")
        # PDF Export Action
        pdf_path = os.path.join(project_root, "reports", "ledgermind_report.pdf")
        if os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()
            st.download_button(
                label="📄  Download Executive Financial Report (PDF)",
                data=pdf_bytes,
                file_name="LedgerMind_Financial_Report.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

        st.write("")
        # 4 Metric Cards
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.markdown(
                f"""
                <div class="metric-card-dev">
                    <div class="metric-top-row">
                        <span class="metric-tag">TOTAL INVOICES</span>
                        <div class="metric-icon-badge metric-icon-blue">📁</div>
                    </div>
                    <div class="metric-main-value">{report.get('total_invoices', 0)}</div>
                    <div class="metric-sub-label">Ledger records processed</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with k2:
            st.markdown(
                f"""
                <div class="metric-card-dev">
                    <div class="metric-top-row">
                        <span class="metric-tag">MATCHED</span>
                        <div class="metric-icon-badge metric-icon-green">✓</div>
                    </div>
                    <div class="metric-main-value">{report.get('matched_count', 0)}</div>
                    <div class="metric-sub-label">Cleared transactions</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with k3:
            st.markdown(
                f"""
                <div class="metric-card-dev">
                    <div class="metric-top-row">
                        <span class="metric-tag">EXCEPTIONS</span>
                        <div class="metric-icon-badge metric-icon-red">⚠</div>
                    </div>
                    <div class="metric-main-value" style="color: #DC2626;">{report.get('exception_count', 0)}</div>
                    <div class="metric-sub-label">Actionable root-causes</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with k4:
            st.markdown(
                f"""
                <div class="metric-card-dev">
                    <div class="metric-top-row">
                        <span class="metric-tag">SETTLEMENT RATIO</span>
                        <div class="metric-icon-badge metric-icon-orange">⚡</div>
                    </div>
                    <div class="metric-main-value" style="color: #FF6B1A;">{report.get('match_percentage', 0.0)}%</div>
                    <div class="metric-sub-label">Auto-reconciliation rate</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.write("")
        c_chart, c_comm = st.columns([3, 2])

        with c_chart:
            st.markdown("##### **Revenue Trajectory & Scikit-Learn Q3 Forecast**")
            if not hist_df.empty and not forecast_df.empty:
                fig = go.Figure()

                # Historical line
                fig.add_trace(go.Scatter(
                    x=hist_df["month"],
                    y=hist_df["revenue"],
                    mode="lines+markers",
                    name="Historical Revenue",
                    line=dict(color="#111827", width=2.5),
                    marker=dict(size=7, color="#111827"),
                    hovertemplate="<b>%{x}</b>: $%{y:,.0f}<extra>Historical</extra>"
                ))

                # Projection bridge
                fig.add_trace(go.Scatter(
                    x=[hist_df["month"].iloc[-1], forecast_df["month"].iloc[0]],
                    y=[hist_df["revenue"].iloc[-1], forecast_df["predicted_revenue"].iloc[0]],
                    mode="lines",
                    name="Bridge",
                    line=dict(color="#FF6B1A", width=2, dash="dot"),
                    showlegend=False,
                    hoverinfo="skip"
                ))

                # Forecast line
                fig.add_trace(go.Scatter(
                    x=forecast_df["month"],
                    y=forecast_df["predicted_revenue"],
                    mode="lines+markers",
                    name="Q3 Linear Projection",
                    line=dict(color="#FF6B1A", width=2.5, dash="dash"),
                    marker=dict(size=8, symbol="diamond", color="#EA580C"),
                    hovertemplate="<b>%{x}</b>: $%{y:,.0f}<extra>Forecast</extra>"
                ))

                fig.update_layout(
                    paper_bgcolor="#FFFFFF",
                    plot_bgcolor="#FFFFFF",
                    margin=dict(l=20, r=20, t=25, b=20),
                    height=300,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    xaxis=dict(gridcolor="#F3F4F6", linecolor="#E5E7EB", title=None),
                    yaxis=dict(gridcolor="#F3F4F6", linecolor="#E5E7EB", title=None, tickprefix="$"),
                )
                st.plotly_chart(fig, use_container_width=True)

        with c_comm:
            st.markdown("##### **Executive Strategic Commentary**")
            summary_text = report.get("forecast_summary", "No commentary generated.")
            st.markdown(
                f"""
                <div class="terminal-card">
                    <div class="terminal-topbar">
                        <div class="terminal-dots">
                            <span class="dot dot-green"></span>
                            <span class="dot dot-yellow"></span>
                            <span class="dot dot-green"></span>
                        </div>
                        <span class="terminal-title">agent:forecast-commentary // synthesis</span>
                    </div>
                    <div class="terminal-body" style="font-size: 0.84rem; line-height: 1.6;">
                        <span class="terminal-prompt">$</span> <span class="terminal-highlight">forecast.analyze(q3_projection)</span><br><br>
                        {summary_text}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.write("")
        st.markdown("##### **Granular Ledger Inspection**")
        tab_m, tab_e, tab_f = st.tabs(["⚖️ Matched Records", "🚨 Exceptions", "🔮 Forecast Matrix"])
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
    '<div class="dev-footer">LEDGERMIND AI // AUTONOMOUS MULTI-AGENT FINANCE CONTROLLER // POWERED BY LANGGRAPH &amp; GEMINI</div>',
    unsafe_allow_html=True,
)
