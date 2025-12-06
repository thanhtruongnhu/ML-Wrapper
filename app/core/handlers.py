from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
from .exceptions import AppException
from .logger import get_logger

logger = get_logger(__name__)

# All errors should follow this structure when returned to clients (stable API):
def serialize_app_exception(exc: AppException, request_id: str | None = None):
    payload = {
        "error": {
            "code": exc.code,
            "message": exc.message,
            "details": exc.details or {},
            "request_id": request_id,
        }
    }
    return payload


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        request_id = getattr(request.state, "request_id", None)
        logger.warning("Application error occurred", extra={"request_id": request_id, "code": exc.code})
        return JSONResponse(status_code=exc.status_code, content=serialize_app_exception(exc, request_id))


    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc):
        request_id = getattr(request.state, "request_id", None)
        payload = {"error": {"code": "not_found", "message": "Not found", "request_id": request_id}}
        return JSONResponse(status_code=404, content=payload)


    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        # Development: include repr(exc) or traceback
        detail = exc.args[0] if exc.args else repr(exc)
        request_id = getattr(request.state, "request_id", None)
        logger.error("Unhandled exception", extra={"request_id": request_id, "exc": detail})

        # Do NOT leak internal details in production
        payload = {"error": {"code": "Exception", "message": detail, "request_id": request_id}}
        return JSONResponse(status_code=400, content=payload)


    @app.exception_handler(KeyError)
    async def general_exception_handler_2(request: Request, exc: KeyError):
        detail = exc.args[0] if exc.args else repr(exc)

        return JSONResponse(
            status_code=400,
            content={
                "error": "Server Error",
                "detail": detail
            }
        )