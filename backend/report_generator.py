"""
backend/report_generator.py — Executive Financial PDF Report Generator
=======================================================================
Generates a multi-section PDF financial report using ReportLab,
incorporating reconciliation metrics, AI exception root-causes, and
revenue forecasts with executive commentary.
"""

import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
import pandas as pd

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
    HRFlowable,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY


# ---------------------------------------------------------------------------
# 1. Helper to ensure string and directory safety
# ---------------------------------------------------------------------------
def _ensure_dir(filepath: str) -> None:
    """Ensure the target parent directory exists."""
    parent = os.path.dirname(filepath)
    if parent and not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)


# ---------------------------------------------------------------------------
# 2. Main PDF Generation Function
# ---------------------------------------------------------------------------
def generate_pdf_report(
    final_report: Dict[str, Any],
    exceptions_data: Optional[Union[pd.DataFrame, List[Dict[str, Any]]]] = None,
    output_path: str = "reports/ledgermind_report.pdf",
) -> str:
    """
    Creates a comprehensive PDF financial report using ReportLab.

    Parameters
    ----------
    final_report : dict
        Dictionary containing executive summary metrics and forecast info:
        - `total_invoices`: int
        - `matched_count`: int
        - `unmatched_count`: int
        - `match_percentage`: float
        - `exception_count`: int
        - `forecast_values`: list of dicts [{'month': ..., 'predicted_revenue': ...}]
        - `forecast_summary`: str
        Or a full LangGraph state dict containing `final_report` and `exceptions`.
    exceptions_data : pd.DataFrame or list of dicts, optional
        Exception records with columns/keys: `invoice_id`, `amount`, `explanation`.
        If None, attempts to extract from `final_report.get('exceptions')`.
    output_path : str, default='reports/ledgermind_report.pdf'
        Output file path for the PDF.

    Returns
    -------
    str
        Absolute file path of the generated PDF report.
    """
    # Step 1: Normalize input parameters if passed a LangGraph state dictionary
    if "final_report" in final_report and isinstance(final_report["final_report"], dict):
        report_meta = final_report["final_report"]
        if exceptions_data is None and "exceptions" in final_report:
            exceptions_data = final_report["exceptions"]
    else:
        report_meta = final_report

    # Ensure output directory exists
    _ensure_dir(output_path)

    # Step 2: Initialize ReportLab Document Template
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    # Step 3: Setup Styles
    styles = getSampleStyleSheet()
    
    # Custom Color Palette
    PRIMARY = colors.HexColor("#1E1B4B")     # Deep Indigo
    ACCENT = colors.HexColor("#4F46E5")      # Vibrant Indigo
    SUCCESS = colors.HexColor("#059669")     # Emerald Green
    DANGER = colors.HexColor("#DC2626")      # Crimson
    TEXT_DARK = colors.HexColor("#1E293B")   # Slate 800
    TEXT_MUTED = colors.HexColor("#64748B")  # Slate 500
    BG_LIGHT = colors.HexColor("#F8FAFC")    # Slate 50
    BG_HEADER = colors.HexColor("#F1F5F9")   # Slate 100
    BORDER_COLOR = colors.HexColor("#CBD5E1")# Slate 300

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=PRIMARY,
        spaceAfter=4,
    )

    tagline_style = ParagraphStyle(
        "DocTagline",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13,
        textColor=TEXT_MUTED,
        spaceAfter=12,
    )

    h2_style = ParagraphStyle(
        "SectionHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=PRIMARY,
        spaceBefore=14,
        spaceAfter=8,
    )

    body_style = ParagraphStyle(
        "BodyDark",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=TEXT_DARK,
    )

    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=PRIMARY,
        alignment=TA_LEFT,
    )

    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=TEXT_DARK,
    )

    commentary_style = ParagraphStyle(
        "CommentaryText",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8.5,
        leading=13,
        textColor=PRIMARY,
    )

    kpi_title_style = ParagraphStyle(
        "KPITitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=TEXT_MUTED,
        alignment=TA_CENTER,
    )

    kpi_val_style = ParagraphStyle(
        "KPIVal",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=18,
        textColor=PRIMARY,
        alignment=TA_CENTER,
    )

    kpi_val_green = ParagraphStyle(
        "KPIValGreen",
        parent=kpi_val_style,
        textColor=SUCCESS,
    )

    kpi_val_red = ParagraphStyle(
        "KPIValRed",
        parent=kpi_val_style,
        textColor=DANGER,
    )

    story = []

    # -----------------------------------------------------------------------
    # Section: Header & Metadata
    # -----------------------------------------------------------------------
    story.append(Paragraph("LedgerMind AI — Financial Reconciliation Report", title_style))
    gen_time = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    story.append(
        Paragraph(
            f"Autonomous Financial Controller &bull; Report Generated: <b>{gen_time}</b>",
            tagline_style,
        )
    )
    story.append(HRFlowable(width="100%", thickness=1.5, color=ACCENT, spaceAfter=14))

    # -----------------------------------------------------------------------
    # Section 1: Executive Summary KPIs
    # -----------------------------------------------------------------------
    story.append(Paragraph("1. Executive Summary", h2_style))

    total_inv = report_meta.get("total_invoices", 0)
    matched_cnt = report_meta.get("matched_count", 0)
    unmatched_cnt = report_meta.get("unmatched_count", 0)
    match_pct = report_meta.get("match_percentage", 0.0)

    kpi_data = [
        [
            Paragraph("TOTAL PROCESSED", kpi_title_style),
            Paragraph("MATCHED INVOICES", kpi_title_style),
            Paragraph("UNMATCHED / EXCEPTIONS", kpi_title_style),
            Paragraph("RECONCILIATION RATE", kpi_title_style),
        ],
        [
            Paragraph(str(total_inv), kpi_val_style),
            Paragraph(str(matched_cnt), kpi_val_green),
            Paragraph(str(unmatched_cnt), kpi_val_red),
            Paragraph(f"{match_pct}%", kpi_val_green if match_pct >= 80 else kpi_val_style),
        ],
    ]

    kpi_table = Table(kpi_data, colWidths=[130, 130, 130, 140])
    kpi_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), BG_LIGHT),
            ("BOX", (0, 0), (-1, -1), 1, BORDER_COLOR),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ])
    )
    story.append(kpi_table)
    story.append(Spacer(1, 14))

    # -----------------------------------------------------------------------
    # Section 2: Exceptions Table
    # -----------------------------------------------------------------------
    story.append(Paragraph("2. Reconciliation Exceptions & Root-Cause Intelligence", h2_style))

    # Normalize exceptions dataframe or list
    exc_list = []
    if isinstance(exceptions_data, pd.DataFrame):
        exc_list = exceptions_data.to_dict(orient="records")
    elif isinstance(exceptions_data, list):
        exc_list = exceptions_data

    if exc_list:
        exc_table_data = [
            [
                Paragraph("Invoice ID", table_header_style),
                Paragraph("Amount", table_header_style),
                Paragraph("Status", table_header_style),
                Paragraph("AI Root-Cause Explanation & Recommended Action", table_header_style),
            ]
        ]

        for item in exc_list:
            inv_id = str(item.get("invoice_id", "N/A"))
            amt_val = item.get("amount", 0)
            formatted_amt = f"${amt_val:,.2f}" if isinstance(amt_val, (int, float)) else str(amt_val)
            expl = str(item.get("explanation", "Unmatched transaction requiring manual investigation."))

            exc_table_data.append([
                Paragraph(f"<b>{inv_id}</b>", table_cell_style),
                Paragraph(formatted_amt, table_cell_style),
                Paragraph("<font color='#DC2626'><b>UNMATCHED</b></font>", table_cell_style),
                Paragraph(expl, table_cell_style),
            ])

        exc_table = Table(exc_table_data, colWidths=[75, 65, 75, 315])
        exc_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), BG_HEADER),
                ("BOX", (0, 0), (-1, -1), 1, BORDER_COLOR),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ])
        )
        story.append(exc_table)
    else:
        story.append(
            Paragraph(
                "<i>No unmatched exceptions detected. 100% of invoice transactions matched corresponding bank records.</i>",
                body_style,
            )
        )

    story.append(Spacer(1, 14))

    # -----------------------------------------------------------------------
    # Section 3: Cash & Revenue Forecast
    # -----------------------------------------------------------------------
    story.append(Paragraph("3. Revenue Forecast & Strategic Cash Flow Projection", h2_style))

    forecast_items = report_meta.get("forecast_values", [])
    if forecast_items:
        forecast_table_data = [
            [
                Paragraph("Target Period", table_header_style),
                Paragraph("Projected Revenue (USD)", table_header_style),
                Paragraph("Model Method", table_header_style),
            ]
        ]
        for f in forecast_items:
            m_label = str(f.get("month", "Next Period"))
            p_val = f.get("predicted_revenue", 0)
            forecast_table_data.append([
                Paragraph(f"<b>{m_label}</b>", table_cell_style),
                Paragraph(f"${p_val:,}", table_cell_style),
                Paragraph("Scikit-Learn Linear Regression", table_cell_style),
            ])

        forecast_table = Table(forecast_table_data, colWidths=[130, 200, 200])
        forecast_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), BG_HEADER),
                ("BOX", (0, 0), (-1, -1), 1, BORDER_COLOR),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ])
        )
        story.append(forecast_table)
        story.append(Spacer(1, 8))

    # Forecast Commentary Box
    summary_text = report_meta.get("forecast_summary", "No forecast commentary available.")
    commentary_data = [
        [
            Paragraph(
                f"<b>Executive Strategic Synthesis:</b><br/>{summary_text}",
                commentary_style,
            )
        ]
    ]
    commentary_box = Table(commentary_data, colWidths=[530])
    commentary_box.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EEF2FF")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#C7D2FE")),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ])
    )
    story.append(commentary_box)

    # -----------------------------------------------------------------------
    # Footer Note
    # -----------------------------------------------------------------------
    story.append(Spacer(1, 18))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER_COLOR, spaceAfter=8))
    story.append(
        Paragraph(
            "<font size='7' color='#94A3B8'>Confidential &bull; Prepared by LedgerMind AI Autonomous Financial System &bull; For internal corporate financial management only.</font>",
            ParagraphStyle("DocFooter", parent=styles["Normal"], alignment=TA_CENTER),
        )
    )

    # Step 4: Build Document
    doc.build(story)
    return os.path.abspath(output_path)


# ---------------------------------------------------------------------------
# 3. Standalone Test Runner
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    from backend.graph import run_pipeline

    print("=" * 65)
    print("  LedgerMind AI — Generating PDF Financial Report")
    print("=" * 65)

    invoice_file = "data/invoice.csv"
    bank_file = "data/bank.csv"
    revenue_file = "data/revenue.csv"

    state = run_pipeline(invoice_file, bank_file, revenue_file)
    pdf_path = generate_pdf_report(state, output_path="reports/ledgermind_report.pdf")

    print(f"\n✅ PDF Report successfully generated at:\n   {pdf_path}")
    print(f"   File size: {os.path.getsize(pdf_path)} bytes")
    print("=" * 65)
