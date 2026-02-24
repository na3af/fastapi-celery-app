import os
import time
from functools import wraps
from app.celery_app import celery_app
from app.errors import TaskError, PathNotFoundError, InvalidInputError


def handle_task_errors(func):
    """Decorator that catches TaskError and stores it properly in Redis."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return {"success": True, "data": result}
        except TaskError as e:
            return {
                "success": False,
                "error": {
                    "code": e.code,
                    "message": e.message,
                    "details": e.details,
                },
            }
    return wrapper


@celery_app.task
@handle_task_errors
def add_numbers(a: int, b: int) -> int:
    """Simple task that adds two numbers."""
    time.sleep(2)
    return a + b


@celery_app.task
@handle_task_errors
def process_file(file_path: str) -> dict:
    """Process a file - raises error when path doesn't exist."""
    time.sleep(1)

    if not os.path.exists(file_path):
        raise PathNotFoundError(path=file_path)

    if not os.path.isfile(file_path):
        raise InvalidInputError(
            message=f"Path is not a file: {file_path}",
            details={"path": file_path},
        )

    file_size = os.path.getsize(file_path)
    return {
        "path": file_path,
        "size": file_size,
        "processed": True,
    }
