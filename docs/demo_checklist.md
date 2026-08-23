# 📋 LedgerMind AI — Pre-Demo Checklist

Use this checklist before walking up to present or record the live demonstration.

---

### 🔌 Hardware & Environment
- [ ] Laptop fully charged + power adapter packed.
- [ ] Phone mobile hotspot tested and ready in case venue Wi-Fi is unstable (needed for Gemini API calls).
- [ ] Screen resolution set appropriately (1080p recommended for clean projection).

---

### 💻 Codebase & Service Health
- [ ] Virtual environment activated (`.\venv\Scripts\activate` or standard Python environment).
- [ ] Streamlit web server running and tested:
  ```bash
  streamlit run frontend/app.py
  ```
- [ ] `.env` file present in root with valid `GEMINI_API_KEY`.
- [ ] PostgreSQL / SQLite database connection verified (`🟢 DB: Connected` badge visible).
- [ ] ChromaDB vector store present at `chroma_db/` with 8 ingested chunks (`python rag_ingest.py` executed).

---

### 📂 Datasets & Artifacts
- [ ] `data/invoice.csv` (50 rows) and `data/bank.csv` (40 rows) present and unmodified.
- [ ] `data/revenue.csv` (6 months) present.
- [ ] PDF report generation verified in the last hour (`python report_generator.py`).
- [ ] Browser tab open to `http://localhost:8501`, refreshed and responsive.

---

### 🛡️ Fallback & Contingency
- [ ] Backup screen recording video saved locally on desktop.
- [ ] Backup screenshots of all 3 tabs (Dashboard, AI Copilot, Full Pipeline) stored in a local folder.
- [ ] `docs/judge_qa.md` reviewed for spontaneous Q&A.
