from fastapi import FastAPI, Depends, HTTPException
from .routers.auth import router as auth_router
from .routers.tasks import router as task_router
from .database import engine, Base
from .models import user
import structlog
from structlog.stdlib import LoggerFactory
from structlog.contextvars import bind_contextvars, clear_contextvars
import uuid
from .exceptions import global_exception_handler, http_exception_handler

structlog.configure(
    logger_factory=LoggerFactory(),
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)

log = structlog.get_logger()
app = FastAPI()

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

app.include_router(auth_router)
app.include_router(task_router)


log.info("SYSTEM INITIALIZED", status="OK")

@app.middleware("http")
async def request_id_middleware(request, call_next):
    clear_contextvars()
    bind_contextvars(request_id = str(uuid.uuid4()))
    response = await call_next(request)
    return response

@app.get("/health")
async def health_check():
    return {"status": "ok"}

