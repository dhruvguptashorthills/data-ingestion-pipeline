import redis
import json

redis_client = redis.Redis(host="localhost", port=6379, db=1)

def update_progress(task_id: str, data: dict):
    redis_client.set(task_id, json.dumps(data))

def get_progress(task_id: str) -> dict:
    raw = redis_client.get(task_id)
    return json.loads(raw) if raw else {"status": "PENDING", "task_id": task_id}
