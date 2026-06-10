from fastapi import FastAPI, Depends, HTTPException
from .routers.tasks import router as task_router
from .database import engine, Base
import logging
import sys
import structlog
from structlog.stdlib import LoggerFactory
from structlog.contextvars import bind_contextvars, clear_contextvars
import uuid
from .exceptions import global_exception_handler, http_exception_handler
from prometheus_fastapi_instrumentator import Instrumentator
from .metrics import tasks_created_total, cache_hits_total, cache_misses_total
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.grpc import GrpcInstrumentorClient

provider = TracerProvider(resource=Resource.create({"service.name": "task-service"}))
exporter = OTLPSpanExporter(endpoint="http://jaeger:4317", insecure=True)
provider.add_span_processor(BatchSpanProcessor(exporter))
trace.set_tracer_provider(provider)
GrpcInstrumentorClient().instrument()

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

log = structlog.get_logger()
app = FastAPI()

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

app.include_router(task_router)

Instrumentator().instrument(app).expose(app)
FastAPIInstrumentor().instrument_app(app)

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

