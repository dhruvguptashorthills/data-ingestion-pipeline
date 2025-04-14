from src.celery_app import celery_app
from src.llama_parser.llama_resume_parser import ResumeParser

@celery_app.task(bind=True)
def parse_resumes_task(self):
    from src.utils.progress import update_progress
    from datetime import datetime

    task_id = self.request.id
    try:
        update_progress(task_id, {
            "task_id": task_id,
            "status": "starting",
            "started_at": datetime.utcnow().isoformat()
        })
        ResumeParser().run_with_progress(task_id)
        return {"status": "success"}
    except Exception as e:
        update_progress(task_id, {
            "task_id": task_id,
            "status": "error",
            "error": str(e)
        })
        return {"status": "error", "message": str(e)}
