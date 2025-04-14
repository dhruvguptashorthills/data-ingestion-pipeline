from src.celery_app import celery_app
from src.standardizer.standardizer import ResumeStandardizer
import asyncio

@celery_app.task(bind=True)
def standardize_resumes_task(self):
    from src.utils.progress import update_progress
    from datetime import datetime

    task_id = self.request.id
    update_progress(task_id, {
        "task_id": task_id,
        "status": "starting",
        "phase": "standardizing",
        "started_at": datetime.utcnow().isoformat()
    })

    try:
        asyncio.run(ResumeStandardizer().run_with_progress(task_id))
        return {"status": "success", "message": "Standardization complete"}
    except Exception as e:
        update_progress(task_id, {
            "task_id": task_id,
            "status": "error",
            "phase": "standardizing",
            "error": str(e)
        })
        return {"status": "error", "message": str(e)}
