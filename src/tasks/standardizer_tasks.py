# tasks/standardizer_tasks.py
from src.celery_app import celery_app
from src.standardizer.standardizer import ResumeStandardizer
import asyncio

@celery_app.task
def standardize_resumes_task():
    try:
        asyncio.run(ResumeStandardizer().run())
        return {"status": "success", "message": "Standardization complete"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
