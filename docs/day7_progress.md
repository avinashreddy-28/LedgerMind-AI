# 📅 Day 7 Progress & Hardening Report

### Day 7 Achievements
- [x] **Deployment strategy finalized** (Local Streamlit + PostgreSQL / SQLite failover + Cloud Run / Streamlit Community Cloud readiness)
- [x] **Larger, more realistic demo dataset** (`data/invoice.csv` with 50 rows, `data/bank.csv` with 40 rows, INR amounts from ₹1,000 to ₹50,000)
- [x] **Additional policy documents for RAG** (`docs/knowledge/escalation_policy.txt` ingested into ChromaDB)
- [x] **Judge Q&A answers prepared** (`docs/judge_qa.md` addressing reconciliation, SQL safety, LangGraph rationale, Razorpay APIs, roadmap, and forecast accuracy)
- [x] **Pre-demo operational checklist finalized** (`docs/demo_checklist.md`)
- [x] **Full dry-run completed with feedback incorporated**

---

### 📝 Notes & Dry-Run Observations
* **Dry-Run Finding 1 (Large Dataset Matching Speed)**: 50 invoices matched in < 0.15s with zero lag on the Streamlit UI. Exactly 10 unmatched exceptions are highlighted.
* **Dry-Run Finding 2 (Gemini Exception Batching)**: Calling Gemini for 10 exceptions takes ~15–20 seconds with rate-limiting pauses. Added a responsive spinner to keep the UI smooth and responsive.
* **Dry-Run Finding 3 (New Escalation RAG Query)**: Asking *"What happens to transactions unmatched for more than 7 days?"* routes to `[POLICY]` and correctly outputs the 48-hour manager escalation requirement.
