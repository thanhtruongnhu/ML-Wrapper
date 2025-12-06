from typing import Any, Mapping, Optional


class AppException(Exception):
    """Base application exception. Use subclasses for known failure modes.
    Attributes:
    code: short machine-readable error code
    message: human-readable message
    details: optional extra structured data
    status_code: HTTP status code to return
    """
    code: str = "app_error"
    message: str = "An application error occurred"
    status_code: int = 500


    def __init__(self, message: Optional[str] = None, details: Optional[Mapping[str, Any]] = None):
        if message:
            self.message = message
        self.details = details
        super().__init__(self.message)

# subclasses:
class BadRequest(AppException):
    code = "bad_request"
    status_code = 400


class NotFound(AppException):
    code = "not_found"
    status_code = 404


class PredictionTimeout(AppException):
    code = "prediction_timeout"
    status_code = 504


class ModelUnavailable(AppException):
    code = "model_unavailable"
    status_code = 503
