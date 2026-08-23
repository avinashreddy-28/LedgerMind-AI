# 📒 LedgerMind AI
> **An Autonomous Finance Controller for Reconciliation, Forecasting & Exception Intelligence**

LedgerMind AI is an autonomous, multi-agent financial operations platform that replaces manual monthly close workflows. It ingests invoice registers and bank statements, reconciles transactions, diagnoses exception root causes using Google Gemini, forecasts quarterly cash flow with Scikit-Learn, answers data & policy queries via a natural language router, and exports board-ready executive PDF reports.

---

## 🌟 Key Features

* **⚖️ Automated Transaction Matching Engine**: Ingests invoice registers and bank statements, matching transactions by amount and date with exact consumption logic.
* **🧠 Gemini Root-Cause Exception Intelligence**: Identifies mismatch reasons (e.g. split wires, processing fees, unlinked deposits) and generates actionable remediation guidance.
* **🤖 Multi-Agent Query Router & Copilot**:
  * **Text-to-SQL Copilot**: Converts natural English queries to read-only SQL executed against PostgreSQL/SQLite with AST safety guards.
  * **Policy RAG Agent**: Uses ChromaDB vector search across company finance manuals with strictly grounded Gemini answers.
* **📈 ML Revenue & Cash Forecasting**: Fits a `scikit-learn` Linear Regression model on historical revenue data and synthesizes executive strategic commentary.
* **🚀 LangGraph Sequential Orchestration**: Chains all 5 operational nodes (`load_node` ➔ `reconciliation_node` ➔ `exception_node` ➔ `forecast_node` ➔ `report_node`).
* **📑 ReportLab PDF Generator**: Compiles metrics, exception tables, and forecast charts into downloadable, board-ready executive PDF reports.
* **🎨 Modern Streamlit UI**: Dark-mode glassmorphic interface with metric cards, tabbed views, Plotly charts, and PDF download.

---

## 🏛️ Architecture & Agent Graph

```
                       ┌───────────────────────────────┐
                       │    Streamlit Web Dashboard    │
                       │    (Dashboard / Copilot / UI) │
                       └──────────────┬────────────────┘
                                      │
               ┌──────────────────────┴──────────────────────┐
               ▼                                             ▼
┌──────────────────────────────┐              ┌──────────────────────────────┐
│       AI Query Router        │              │  LangGraph 5-Node Pipeline   │
│   (DATA vs. POLICY Parser)   │              │   (End-to-End Orchestrator)  │
└──────┬────────────────┬──────┘              └──────────────┬───────────────┘
       │                │                                    │
       ▼                ▼                                    ▼
┌──────────────┐ ┌──────────────┐             ┌──────────────────────────────┐
│  SQL Copilot │ │  Policy RAG  │             │ 1. Data Ingestion Node       │
│  (Text-to-SQL│ │  (ChromaDB + │             │ 2. Reconciliation Node       │
│  PostgreSQL) │ │  Grounding)  │             │ 3. Gemini Exception Node     │
└──────────────┘ └──────────────┘             │ 4. Scikit-Learn Forecast Node│
                                              │ 5. Executive Report Node     │
                                              └──────────────┬───────────────┘
                                                             ▼
                                              ┌──────────────────────────────┐
                                              │ ReportLab PDF Generator (PDF)│
                                              └──────────────────────────────┘
```

---

## 📂 Project Structure

```
LedgerMind-AI/
├── backend/
│   ├── reconciliation.py     # Transaction matching & DB persistence
│   ├── exception_agent.py    # Gemini root-cause exception analysis
│   ├── copilot_agent.py      # Natural language Text-to-SQL engine
│   ├── rag_agent.py          # ChromaDB policy document search & grounding
│   ├── router_agent.py       # Single-token DATA vs. POLICY classifier
│   ├── forecast_agent.py     # Scikit-Learn regression & commentary
│   ├── graph.py              # LangGraph sequential pipeline
│   ├── report_generator.py   # ReportLab executive PDF generator
│   └── db.py                 # PostgreSQL & SQLite database engine
├── frontend/
│   └── app.py                # Streamlit tabbed dashboard & visualization
├── data/
│   ├── invoice.csv           # Sample invoice register
│   ├── bank.csv              # Sample bank transaction statement
│   └── revenue.csv           # Historical revenue data
├── docs/knowledge/
│   ├── settlement_policy.txt # Merchant settlement rules
│   ├── refund_policy.txt     # Customer refund guidelines
│   └── finance_operations_manual.txt # Escalation procedures
├── rag_ingest.py             # ChromaDB vector store ingestion script
├── requirements.txt          # Python dependencies
├── DEMO_SCRIPT.md            # 3-Minute live presentation script
└── README.md
```

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/avinashreddy-28/LedgerMind-AI.git
cd LedgerMind-AI
```

### 2. Set Up Virtual Environment & Dependencies
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ledgermind_db  # optional: falls back to SQLite
```

### 4. Ingest Policy Knowledge Base
```bash
python rag_ingest.py
```

### 5. Launch the Streamlit Dashboard
```bash
streamlit run frontend/app.py
```
Open `http://localhost:8501` in your browser.

---

## 🧪 Testing & Standalone Execution

* **Full LangGraph Pipeline**:
  ```bash
  python graph.py
  ```
* **PDF Report Generation**:
  ```bash
  python report_generator.py
  ```
* **Multi-Agent Query Router**:
  ```bash
  python router_agent.py
  ```
* **Revenue Forecaster**:
  ```bash
  python forecast_agent.py
  ```

---

## 📄 License
MIT License. Built for modern financial teams by LedgerMind AI.
