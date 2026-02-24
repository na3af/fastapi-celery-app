from enum import Enum


class ErrorCode(str, Enum):
    PATH_NOT_FOUND = "PATH_NOT_FOUND"
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    INVALID_INPUT = "INVALID_INPUT"
    TASK_FAILED = "TASK_FAILED"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class TaskError(Exception):
    """Custom exception that serializes properly for Celery/Redis."""

    def __init__(self, code, message: str, details: dict = None):
        self.code = code.value if isinstance(code, ErrorCode) else code
        self.message = message
        self.details = details if details is not None else {}
        # Store in args for proper pickling
        super().__init__(self.code, self.message, self.details)

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details,
        }


class PathNotFoundError(TaskError):
    def __init__(self, path: str):
        super().__init__(
            code=ErrorCode.PATH_NOT_FOUND,
            message=f"Path does not exist: {path}",
            details={"path": path},
        )


class FileNotFoundError(TaskError):
    def __init__(self, filename: str):
        super().__init__(
            code=ErrorCode.FILE_NOT_FOUND,
            message=f"File not found: {filename}",
            details={"filename": filename},
        )


class InvalidInputError(TaskError):
    def __init__(self, message: str, details: dict = None):
        super().__init__(
            code=ErrorCode.INVALID_INPUT,
            message=message,
            details=details,
        )
