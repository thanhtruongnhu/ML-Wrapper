from contextlib import asynccontextmanager
from fastapi import FastAPI
import asyncio
from app.core.handlers import register_exception_handlers
from app.core.middleware import request_id_and_timing_middleware, safe_fallback_middleware
from app.routers import predict, health, getError
from app.services.gc_tuning import gc_background_worker

# Why do we need GC Background worker?
# Reason: As Python Automatic GC runs at unpredictable times - often during API request -> we need GC Background worker to run GC outside request handling in the background to avoid any added latency during request time
@asynccontextmanager
async def lifespan(app: FastAPI):
    gc_task = asyncio.create_task(gc_background_worker())

    try:
        yield # Application runs here
    finally:
        gc_task.cancel() #Sends a cancellation request to the coroutine. The coroutine receives a CancelledError at the next await (within request handling)
        try:
            await gc_task #Waits for the coroutine to exit cleanly after receiving the cancellation. Ensures all resources inside the task are released (memory, file handles, logging, etc.) -> avoid weird errors from dangling tasks
        except asyncio.CancelledError:
            pass


app = FastAPI(lifespan=lifespan)

# When an error is thrown, FastAPI will:
# 1. look for an exception handler registered for ValueError
# 2. if none → look for a handler for Exception
# 3. if none → propagate to outer middleware / crash
# This is why typed handling works.

# # Example: placing a runtime error inside a middleware. As safe_fallback_middleware is placed at last, this runtime error WILL be caught and sanitized
# @app.middleware("http")
# async def buggy_middleware(request, call_next):
#     raise RuntimeError("Middleware failed")


# PART I: Middlewares
# MIDDLEWARE is best for logging, measuring latency
# Middleware 1: latency
app.middleware("http")(request_id_and_timing_middleware)

# Use MIDDLEWARE to catch everything in the request pipeline (Infrastructure-Level errors), including:
# errors thrown before the route
# errors after the response returned
# errors in start up/ shut  down event
# errors thrown in dependencies
# errors in middleware itself
# middleware 2: fallback that converts non-AppException to sanitized 500
app.middleware("http")(safe_fallback_middleware)
# Note: MUST place safe_fallback_middleware at last among all middlewares as we wanna sanitize all runtime errors


# PART II: Exception Handler
# Use EXCEPTION HANDLER to catch Route-Level errors. Using this because:
# distinguish between ValueError and KeyError
# return correct HTTP status codes
# integrate with OpenAPI
# provide typed error handling

# Additional notes:
#       can't use "asyncio.run(register_exception_handlers(app))" because:
#       FastAPI (via uvicorn) already runs inside an async event loop. We CANNOT create another async event loop inside another one!
register_exception_handlers(app)



app.include_router(predict.router)
app.include_router(health.router)
app.include_router(getError.router)




@app.get("/")
async def root():
    return {"message": "App is running!"}