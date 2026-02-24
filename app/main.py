from fastapi import FastAPI
from app.celery_app import celery_app
from app.tasks import add_numbers, process_file

app = FastAPI(title="FastAPI + Celery Demo")


@app.get("/")
def root():
    return {"message": "FastAPI + Celery Demo"}


@app.post("/tasks/add")
def create_add_task(a: int, b: int):
    """Submit an addition task to Celery."""
    task = add_numbers.delay(a, b)
    return {"task_id": task.id, "status": "submitted"}


@app.post("/tasks/process-file")
def create_process_file_task(file_path: str):
    """Submit a file processing task to Celery."""
    task = process_file.delay(file_path)
    return {"task_id": task.id, "status": "submitted"}


@app.get("/tasks/{task_id}")
def get_task_status(task_id: str):
    """Get the status and result of a task from Redis."""
    task = celery_app.AsyncResult(task_id)

    response = {
        "task_id": task_id,
        "status": task.status,
    }

    if task.status == "PENDING":
        return response

    if task.ready():
        result = task.result

        if isinstance(result, dict):
            if result.get("success"):
                response["status"] = "SUCCESS"
                response["result"] = result.get("data")
            else:
                response["status"] = "FAILED"
                response["error"] = result.get("error")
        else:
            response["result"] = result

    return response
