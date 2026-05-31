from fastapi import FastAPI, HTTPException
from .routers.auth import router as auth_router
import logging
import sys
import structlog
from structlog.stdlib import LoggerFactory
from structlog.contextvars import bind_contextvars, clear_contextvars
import uuid
from .exceptions import global_exception_handler, http_exception_handler
from contextlib import asynccontextmanager
import threading
from .grpc.server import serve

logging.basicConfig(
    format="%(message)s", 
    stream=sys.stdout, 
    level=logging.INFO,
)

structlog.configure(
    logger_factory=LoggerFactory(),
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    thread = threading.Thread(target=serve, daemon=True)
    thread.start()
    yield

log = structlog.get_logger()
app = FastAPI(lifespan=lifespan)

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

app.include_router(auth_router)

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

