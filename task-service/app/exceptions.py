from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import structlog

log = structlog.get_logger()

async def global_exception_handler(request: Request, exc: Exception):
    log.error("unhandled_exception", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error", "error_code": "500"}
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "error_code": str(exc.status_code)}
    )