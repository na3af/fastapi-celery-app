import os
import time
from app.celery_app import celery_app
from app.errors import TaskError, PathNotFoundError, InvalidInputError


@celery_app.task(bind=True)
def add_numbers(self, a: int, b: int) -> int:
    """Simple task that adds two numbers."""
    time.sleep(2)
    return a + b


@celery_app.task(bind=True)
def process_file(self, file_path: str) -> dict:
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
