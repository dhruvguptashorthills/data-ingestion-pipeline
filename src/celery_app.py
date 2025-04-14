from celery import Celery

celery_app = Celery(
    "resume_tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
)

celery_app.conf.task_track_started = True
celery_app.conf.result_expires = 3600
