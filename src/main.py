from fastapi import FastAPI
from fastapi.responses import JSONResponse
from celery.result import AsyncResult

from src.celery_app import celery_app
from src.tasks import parser_tasks, standardizer_tasks
app = FastAPI()

@app.post("/parse")
def trigger_parse():
    task = parser_tasks.parse_resumes_task.delay()
    return {"task_id": task.id}

@app.post("/standardize")
def trigger_standardize():
    task = standardizer_tasks.standardize_resumes_task.delay()
    return {"task_id": task.id}

@app.get("/status/{task_id}")
def check_status(task_id: str):
    task_result = AsyncResult(task_id, app=celery_app)
    response = {
        "task_id": task_id,
        "status": task_result.status,
    }
    if task_result.status == "SUCCESS":
        response["result"] = task_result.result
    elif task_result.status == "FAILURE":
        response["error"] = str(task_result.result)
    return response
