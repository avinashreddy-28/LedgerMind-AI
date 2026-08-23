# 🎙️ LedgerMind AI — Live Product Demo & Video Presentation Script
**Duration:** ~3 Minutes &bull; **Target Audience:** Finance Executives, Hackathon Judges, Product Leaders  
**Tagline:** *An Autonomous Finance Controller for Reconciliation, Forecasting & Exception Intelligence*

---

## ⏱️ Timeline & Scene-by-Scene Script

```
0:00 ─── [1. Problem] ─── 0:15 ─── [2. Live Upload] ─── 0:45 ─── [3. Reconciliation] ─── 1:05
1:05 ─── [4. AI Exceptions] ─── 1:35 ─── [5. AI Copilot] ─── 2:20 ─── [6. Forecast] ─── 2:40
2:40 ─── [7. Full Pipeline + PDF] ─── 3:00 ─── [8. Closing] ─── 3:15
```

---

### 🎬 Scene 1: The Problem (0:00 – 0:15)
* **Visual:** Browser showing the **LedgerMind AI** Dashboard (`http://localhost:8501`) with the clean top banner.
* **On-Screen Action:** Hover over the header subtitle: *"An Autonomous Finance Controller for Reconciliation, Forecasting & Exception Intelligence"*.
* **Spoken Script (Voiceover):**
  > *"Every month, finance teams spend hundreds of hours manually matching invoices, chasing down missing payments, deciphering mismatched line items, and struggling to forecast cash flow. Today, we're changing that with **LedgerMind AI** — an autonomous multi-agent financial controller that handles this end-to-end in seconds."*

---

### 🎬 Scene 2: Live Ingestion & Upload (0:15 – 0:45)
* **Visual:** Tab 1 — **`📊 Dashboard`** ➔ Transaction Data Ingestion area.
* **On-Screen Action:** Click **"📁 Use Sample Datasets"** (or upload `data/invoice.csv` and `data/bank.csv`).
* **Spoken Script (Voiceover):**
  > *"Let's start on the Dashboard. Ingesting transactions is as simple as dropping in your invoice register and bank statement. I'll load our sample datasets — LedgerMind immediately parses both files, cleans the schemas, and prepares them for automated matching."*

---

### 🎬 Scene 3: Instant Reconciliation Results (0:45 – 1:05)
* **Visual:** KPI Metric Cards + Matched/Unmatched tables appearing instantly.
* **On-Screen Action:** Point cursor across the 4 KPI cards (**Total Invoices: 5**, **Matched: 3**, **Unmatched: 2**, **Match Rate: 60.0%**).
* **Spoken Script (Voiceover):**
  > *"Instantly, our reconciliation engine matches transactions by amount and date. Out of 5 invoices, 3 are perfectly matched ($27,000 reconciled), giving us a 60% match rate. But what about the 2 unmatched invoices? Traditional ERPs leave you with a blank error — LedgerMind goes further."*

---

### 🎬 Scene 4: AI Exception Root-Cause Intelligence (1:05 – 1:35)
* **Visual:** Unmatched Invoices section ➔ AI Exception Intelligence table.
* **On-Screen Action:** Click **"🧠 Explain Exceptions with Gemini"** (or expand invoice `INV003`). Highlight the reasoning and action item.
* **Spoken Script (Voiceover):**
  > *"With one click, our Gemini-powered Exception Agent diagnoses the exact root causes. For example, looking at invoice **INV003** for $12,000, LedgerMind identifies that payment was split across two tranches with a missing wire reference, and advises the controller to check the pending deposit queue before re-billing."*

---

### 🎬 Scene 5: Multi-Agent AI Copilot (1:35 – 2:20)
* **Visual:** Tab 2 — **`🤖 AI Copilot`**.
* **On-Screen Actions:**
  1. Click or type: `"Which invoices are unmatched?"`
  2. Point out: **`Source: 📊 Database`** and answer (**INV003 & INV004**).
  3. Click or type: `"What is the settlement cycle?"`
  4. Point out: **`Source: 📄 Policy Documents`** and answer (**T+2 business days**).
* **Spoken Script (Voiceover):**
  > *"Next, let's switch to the **AI Copilot**. Finance controllers shouldn't have to write SQL or dig through 50-page policy manuals. When I ask, **'Which invoices are unmatched?'**, our Router Agent classifies this as a database query, writes safe SQL, and pulls live data from PostgreSQL.*  
  > *Now, when I ask, **'What is the standard settlement cycle?'**, it automatically routes to our ChromaDB vector store, retrieving our company finance manual to answer that settlements process in T+2 business days with 10 PM cutoffs."*

---

### 🎬 Scene 6: ML Cash & Revenue Forecasting (2:20 – 2:40)
* **Visual:** Tab 3 — **`🚀 Full Pipeline`** ➔ Plotly chart & AI Commentary.
* **On-Screen Action:** Hover over the Plotly line chart (solid cyan historical trend bridging into dashed purple Q3 forecast).
* **Spoken Script (Voiceover):**
  > *"Next is forecasting. Our Forecast Agent runs Linear Regression on historical monthly revenues and projects our Q3 cash trajectory — reaching a projected peak of **$194,667** by September with an average monthly expansion rate of $11,000, accompanied by strategic AI commentary on capital reserves."*

---

### 🎬 Scene 7: Full LangGraph Pipeline & PDF Export (2:40 – 3:00)
* **Visual:** Click **"▶️ Run LedgerMind Pipeline"** ➔ **"📄 Download Full Report (PDF)"**.
* **On-Screen Action:** Click the PDF download button and preview the generated executive report.
* **Spoken Script (Voiceover):**
  > *"Finally, everything is orchestrated through a single LangGraph stateful pipeline. Clicking **'Run LedgerMind Pipeline'** executes all 5 nodes in sequence, auto-persists records to the database, and generates a board-ready executive PDF report complete with KPI tables, AI exception logs, and revenue projections ready to share."*

---

### 🎬 Scene 8: The Close (3:00 – 3:15)
* **Visual:** Back to main dashboard overview with all green status badges visible.
* **Spoken Script (Voiceover):**
  > *"This is **LedgerMind AI** — 5 specialized AI agents, one seamless pipeline, built end-to-end to give finance teams superpowers. Thank you!"*

---

## 📋 Quick Demo Checklist

| Step | Action | Expected Output |
| :--- | :--- | :--- |
| **1. Ingest Data** | Click *"Use Sample Datasets"* | 5 total invoices loaded, 4 KPI cards populate |
| **2. Exception AI** | Click *"Explain Exceptions with Gemini"* | AI root causes appear in the exceptions table |
| **3. Copilot (DB)** | Ask *"Which invoices are unmatched?"* | Tagged with `Source: 📊 Database` & outputs INV003, INV004 |
| **4. Copilot (RAG)**| Ask *"What is the settlement cycle?"* | Tagged with `Source: 📄 Policy Documents` & outputs T+2 |
| **5. Full Pipeline**| Click *"Run LedgerMind Pipeline"* | Plotly chart + AI synthesis + PDF Download ready |
| **6. PDF Report** | Click *"Download Full Report (PDF)"* | Downloads `LedgerMind_Financial_Report.pdf` |
