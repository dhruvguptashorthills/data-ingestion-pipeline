# data-ingestion-pipeline
---

### 🧪 CLI Usage (local module runs)

- `python3 src/llama_parser/llama_resume_parser.py`
- `python3 -m asyncio src/standardizer/standardizer.py`

---

### 🚀 FastAPI + Celery Dev Setup

- `uvicorn src.main:app --reload`
- `celery -A src.celery_worker.celery_app worker --loglevel=info`

--- 

That’s it — clean, minimal, and dev-friendly.