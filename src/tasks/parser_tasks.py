from src.celery_app import celery_app
from src.llama_parser.llama_resume_parser import ResumeParser

@celery_app.task
def parse_resumes_task():
    try:
        ResumeParser().run()
        return {"status": "success", "message": "Parsing complete"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
