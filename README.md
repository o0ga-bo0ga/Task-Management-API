# Task Management API

A production-style RESTful API for managing tasks with user authentication, async background job processing, Redis caching, and Kubernetes deployment. Built as a hands-on project to learn FastAPI, system design, and backend engineering practices.

## Architecture

The system is split into three microservices behind a gateway:

```
Client ──► Gateway (:8000) ──► Auth Service (:8000, :50051 gRPC)
                    │                │
                    │                └──► Auth DB (PostgreSQL)
                    │
                    └──► Task Service (:8000) ──► Task DB (PostgreSQL)
                                        │
                                        ├──► Redis (cache + rate limiting)
                                        │
                                        └──► Celery Worker (async jobs)
                                              │
                                              └──► Webhook (optional callback)
```

- **Gateway** — Single entry point. Verifies JWT on every request (except `/auth/login`, `/auth/register`, `/health`), then proxies to the appropriate upstream service.
- **Auth Service** — User registration, login, JWT issuance. Also exposes a gRPC server on port 50051 for user lookup by email.
- **Task Service** — Task CRUD with Redis caching, Celery-based async notification delivery, Prometheus metrics, and gRPC client for user verification.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI |
| Language | Python 3.11 |
| Database | PostgreSQL 15 (async via asyncpg) |
| ORM | SQLAlchemy 2.0 (async sessions) |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| Cache | Redis |
| Async Jobs | Celery + Redis broker |
| gRPC | grpcio for inter-service user lookup |
| Logging | structlog (structured JSON) |
| Metrics | Prometheus (prometheus-fastapi-instrumentator) |
| Monitoring | Prometheus + Grafana |
| Tests | pytest + aiosqlite (in-memory DB) |
| Linting | Ruff |
| Containerization | Docker + Docker Compose |
| Orchestration | Kubernetes (Minikube) |

## Project Structure

```
task-management-api/
├── gateway/                      # API Gateway
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py               # FastAPI app, JWT verify, reverse proxy
│       └── config.py             # Settings (SECRET_KEY, service URLs)
├── auth-service/                 # Authentication microservice
│   ├── Dockerfile
│   ├── alembic.ini
│   ├── requirements.txt
│   ├── alembic/                  # DB migrations
│   │   └── versions/
│   └── app/
│       ├── main.py               # FastAPI app + gRPC server startup
│       ├── config.py             # Settings (DATABASE_URL, SECRET_KEY)
│       ├── database.py           # Async + sync SQLAlchemy engines
│       ├── dependencies.py       # DB session dependency
│       ├── cache.py              # Redis connection pool
│       ├── limiter.py            # Login rate limiter (5/min per IP)
│       ├── exceptions.py         # Global + HTTP exception handlers
│       ├── models/user.py        # User ORM model
│       ├── schemas/user.py       # Pydantic models (UserCreate, UserResponse)
│       ├── routers/auth.py       # POST /auth/register, /auth/login
│       ├── services/auth_service.py  # Business logic
│       └── grpc/                 # gRPC server (port 50051)
│           ├── server.py
│           ├── auth_pb2.py
│           └── auth_pb2_grpc.py
├── task-service/                 # Task management microservice
│   ├── Dockerfile
│   ├── alembic.ini
│   ├── requirements.txt
│   ├── alembic/                  # DB migrations
│   └── app/
│       ├── main.py               # FastAPI app + Prometheus Instrumentator
│       ├── config.py             # Settings (DB, Redis, Celery URLs)
│       ├── database.py           # Async + sync SQLAlchemy engines
│       ├── dependencies.py       # JWT re-validation + gRPC user lookup
│       ├── cache.py              # Redis connection pool
│       ├── exceptions.py         # Global + HTTP exception handlers
│       ├── worker.py             # Celery app configuration
│       ├── metrics.py            # Prometheus counters
│       ├── models/               # Task + Notification ORM models
│       │   ├── task.py
│       │   └── notification.py
│       ├── schemas/              # Pydantic models
│       │   ├── task.py
│       │   └── notification.py
│       ├── routers/tasks.py      # All /tasks/ endpoints
│       ├── services/             # Business logic
│       │   ├── task_service.py
│       │   └── notification_service.py
│       ├── tasks/notification_tasks.py  # Celery task definitions
│       └── grpc/client.py        # gRPC client -> auth-service:50051
├── k8s/                          # Kubernetes manifests
│   ├── namespace.yml
│   ├── configmap.yml             # Shared config (algorithm, service URLs)
│   ├── secrets.yml               # DB URLs, SECRET_KEY, passwords
│   ├── gateway.yml               # Gateway deployment + NodePort service
│   ├── auth-service.yml          # Auth deployment + ClusterIP service
│   ├── auth-db.yml               # Auth PostgreSQL + PVC
│   ├── task-service.yml          # Task deployment + ClusterIP service
│   ├── task-db.yml               # Task PostgreSQL + PVC
│   └── redis.yml                 # Redis deployment + ClusterIP service
├── proto/auth.proto              # Protobuf definition for gRPC
├── docker-compose.yml            # Local development orchestration
├── prometheus.yml                # Prometheus scrape config
├── ruff.toml                     # Ruff linter configuration
├── pytest.ini                    # Pytest configuration
├── .env.example                  # Environment variable template
└── .github/workflows/ci.yml      # CI pipeline (lint, test, build)
```

## Running Locally with Docker Compose

1. Clone the repository:
   ```bash
   git clone https://github.com/o0ga-bo0ga/Task-Management-API.git
   cd task-api
   ```

2. Create `.env` files for each service from `.env.example`:
   ```bash
   cp .env.example auth-service/.env
   cp .env.example task-service/.env
   cp .env.example gateway/.env
   ```
   Fill in all required variables (database URLs, secret key, etc.).

3. Start all services:
   ```bash
   docker compose up --build
   ```

4. Run database migrations:
   ```bash
   docker compose exec auth-service alembic upgrade head
   docker compose exec task-service alembic upgrade head
   ```

5. Verify:
   ```bash
   curl http://localhost:8082/health
   ```

6. API docs at `http://localhost:8082/docs`

## Deploying on Kubernetes (Minikube)

1. Build images into Minikube's Docker daemon:
   ```bash
   eval $(minikube docker-env)
   docker build --no-cache -t auth-service:latest -f auth-service/Dockerfile auth-service/
   docker build --no-cache -t task-service:latest -f task-service/Dockerfile task-service/
   docker build --no-cache -t gateway:latest -f gateway/Dockerfile gateway/
   ```

2. Apply manifests:
   ```bash
   kubectl apply -f k8s/
   ```

3. Run migrations:
   ```bash
   kubectl exec -n task-platform deploy/auth-service -- alembic upgrade head
   kubectl exec -n task-platform deploy/task-service -- alembic upgrade head
   ```

4. Get the gateway URL:
   ```bash
   minikube service gateway -n task-platform --url
   ```

## API Endpoints

All requests go through the gateway (port 8000, NodePort on Kubernetes).

### Public (no auth required)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login` | Login and receive JWT |

### Authenticated (requires `Authorization: Bearer <token>`)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/tasks/` | Create a task (queues async notification) |
| GET | `/tasks/` | List tasks (paginated, filterable by status) |
| GET | `/tasks/{id}` | Get a single task |
| PUT | `/tasks/{id}` | Update a task |
| DELETE | `/tasks/{id}` | Delete a task |
| GET | `/tasks/notifications` | Get notifications for current user |
| GET | `/tasks/jobs/{job_id}` | Poll Celery job status |

### Query Parameters for `GET /tasks`

- `page` (default: 1) — page number
- `page_size` (default: 10) — items per page
- `status` — filter: `PENDING`, `INPROGRESS`, `COMPLETED`, `CANCELLED`

### Registration

```bash
curl -X POST http://<gateway>/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"yourpassword"}'
```

### Login

```bash
curl -X POST http://<gateway>/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d 'username=user@example.com&password=yourpassword'
```

Login is rate-limited to 5 attempts per minute per IP.

### Create a Task

```bash
curl -X POST http://<gateway>/tasks/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"title":"My Task","description":"Something to do"}'
```

Returns a `job_id` for tracking the async notification.

## Async Job Processing

When a task is created, a Celery worker processes a notification asynchronously:

1. `POST /tasks/` returns immediately with the task data and a `job_id`
2. The Celery worker creates a `Notification` record in the DB
3. If `callback_url` was provided in the task creation, the worker sends a webhook:
   ```json
   {"job_id": "...", "status": "SUCCESS", "user_id": ...}
   ```
4. Poll `GET /tasks/jobs/{job_id}` to check status (`PENDING`, `STARTED`, `SUCCESS`, `FAILURE`)

## Design Decisions

1. **404 for both missing and unauthorized tasks** — Returning 403 for a task the user doesn't own would leak information about other users' data. 404 reveals nothing.

2. **`get_db` uses `try/finally` without `except`** — The dependency only needs to close the session after the request. Catching exceptions here would swallow errors before the global exception handler logs them.

3. **`create_access_token` accepts a dict** — Keeps the function generic with no dependency on the User model. Any payload shape works, making it reusable for refresh tokens or other token types.

4. **`request_id` on every log line** — A middleware generates a UUID per request and binds it to structlog context. Every log event within that request includes the `request_id`, making it easy to trace a single request across all log output.

5. **Celery worker uses sync SQLAlchemy** — Celery tasks run in a separate process with no event loop. Using async sessions would require manual event loop management. A dedicated sync engine is used in the worker process only.

6. **Cache invalidation on mutation** — `PUT` and `DELETE` immediately delete the Redis cache entry for the affected task. A 300-second TTL on cache entries serves as a safety net if invalidation ever fails.

7. **Rate limiting uses `INCR` + conditional `EXPIRE`** — Expiry is set only on the first `INCR` to keep the window fixed from the first request. Setting expiry on every request would reset the window on each attempt.

## Monitoring

- **Prometheus metrics** exposed at `/metrics` on the task service (port 8000)
  - `tasks_created_total` — counter of created tasks
  - `cache_hits_total` / `cache_misses_total` — Redis cache hit/miss counters
  - Plus default FastAPI metrics via `prometheus-fastapi-instrumentator`
- **Grafana** configured in `docker-compose.yml` (port 3000) for visualizing metrics
- **Structured JSON logging** via structlog with `request_id` context for distributed tracing

## Testing

Both auth-service and task-service have pytest test suites using in-memory SQLite (aiosqlite) and a fake Redis implementation:

```bash
# Run auth service tests
cd auth-service && pytest

# Run task service tests
cd task-service && pytest
```

CI pipeline (`.github/workflows/ci.yml`) runs lint (ruff), tests, and Docker builds on push/PR to main.
