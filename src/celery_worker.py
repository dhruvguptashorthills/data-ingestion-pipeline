# celery_worker.py
from src.celery_app import celery_app

celery_app.autodiscover_tasks(['src.tasks'])
