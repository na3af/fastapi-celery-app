from fastapi import FastAPI
from app.celery_app import celery_app
from app.tasks import add_numbers, process_file
from app.errors import TaskError

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

    if task.status == "FAILURE":
        # Task actually failed in Celery - extract error info
        exc = task.result  # This is the exception instance

        if isinstance(exc, TaskError):
            response["error"] = {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            }
        else:
            response["error"] = {
                "code": "INTERNAL_ERROR",
                "message": str(exc),
                "details": {"type": type(exc).__name__},
            }
        return response

    if task.status == "SUCCESS":
        response["result"] = task.result

    return response
