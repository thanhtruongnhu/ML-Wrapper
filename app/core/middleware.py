import time
import uuid
from fastapi import Request
from fastapi.responses import JSONResponse
from .logger import get_logger

logger = get_logger(__name__)

# middleware is a wrapper: [Middleware] → route → exception_handlers → [Middleware]
# We have 2 middlewares:

# Middleware 1: latency
async def request_id_and_timing_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    start = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception as exc:
        # Let exception handlers handle it if registered
        # Re-raise to allow app.exception_handler to pick it up
        logger.exception("Exception bubbled to middleware", extra={"request_id": request_id})
        raise
    finally:
        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.info("request complete",
                    extra={"request_id": request_id, "path": request.url.path, "elapsed_ms": f"{elapsed_ms:.2f}"})

    # attach request id to response headers for correlation
    response.headers["X-Request-ID"] = request_id
    return response


# middleware 2: fallback that converts non-AppException to sanitized 500
async def safe_fallback_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    # By catching only RuntimeError, the middleware is now:
    # 1. allows FastAPI to handle route-level exceptions
    # 2. Avoids shadowing exception handlers -> distinct responsibilities with Exception handlers
    except RuntimeError:
        request_id = getattr(request.state, "request_id", None)
        logger.exception("Unhandled exception in safe_fallback_middleware",
                         extra={"request_id": request_id})
        payload = {"error": {"code": "internal_error", "message": "Internal server error", "request_id": request_id}}
        # errors raised after response start (very rare)
        return JSONResponse({"error": "runtime_error"}, status_code=500)
    # except Exception as exc:
    #     request_id = getattr(request.state, "request_id", None)
    #     logger.exception("Unhandled exception in safe_fallback_middleware",
    #                      extra={"request_id": request_id, "exc": repr(exc)})
    #     payload = {"error": {"code": "internal_error", "message": "Internal server error", "request_id": request_id}}
    #     return JSONResponse(status_code=500, content=payload)
