=# Task Management API

## What is this?
A production-style RESTful API for managing tasks, built from scratch to learn FastAPI, system design, and backend engineering practices. Users can register, authenticate, and manage their own tasks with full CRUD support, async background processing, and Redis caching.

## Tech Stack
- **Python 3.11**
- **FastAPI** — web framework
- **PostgreSQL** — primary database
- **SQLAlchemy (async)** — ORM and query building via asyncpg
- **Alembic** — database migrations
- **Pydantic v2** — request/response validation and settings management
- **passlib + bcrypt** — password hashing
- **python-jose** — JWT encoding and decoding
- **Redis** — caching and rate limiting
- **Celery** — async background task processing
- **structlog** — structured JSON logging
- **pytest** — testing
- **Docker + Docker Compose** — containerization

## Architecture
The codebase follows a three-layer architecture:

- **Routers** — handle HTTP concerns only: parsing requests, calling services, returning responses. No business logic, no direct DB queries.
- **Services** — contain all business logic. Routers call services, services interact with the database.
- **Models** — define the database schema via SQLAlchemy ORM.

This separation means each layer has one job. A router should never know how a password is hashed. A service should never know what HTTP status code to return. This makes the code easier to test, easier to change, and closer to how production codebases are structured.

## Running Locally

1. Clone the repository
   ```bash
   git clone https://github.com/o0ga-bo0ga/Task-Management-API.git
   cd task-api
   ```

2. Create your `.env` file from the example
   ```bash
   cp .env.example .env
   ```
   Fill in all required variables — see `.env.example` for the full list.

3. Start the services
   ```bash
   docker compose up
   ```

4. Run database migrations
   ```bash
   docker compose exec app alembic upgrade head
   ```

5. Verify the app is running
   ```bash
   curl http://localhost:8080/health
   ```

6. Explore the API via Swagger UI at `http://localhost:8080/docs`

## API Endpoints

| Method | Path | Auth Required | Description |
|--------|------|---------------|-------------|
| GET | `/health` | No | Health check |
| POST | `/auth/register` | No | Register a new user |
| POST | `/auth/login` | No | Login and receive JWT |
| POST | `/tasks/` | Yes | Create a task, queues a background notification |
| GET | `/tasks/` | Yes | Get all tasks (paginated, filterable by status) |
| GET | `/tasks/notifications` | Yes | Get all notifications for current user |
| GET | `/tasks/jobs/{job_id}` | Yes | Poll status of a background job |
| GET | `/tasks/{id}` | Yes | Get a single task |
| PUT | `/tasks/{id}` | Yes | Update a task |
| DELETE | `/tasks/{id}` | Yes | Delete a task |

### Query Parameters for `GET /tasks`
- `page` (default: 1)
- `page_size` (default: 10)
- `status` — filter by task status: `PENDING`, `INPROGRESS`, `COMPLETED`, `CANCELLED`

### Optional Body Parameters for `POST /tasks/`
- `callback_url` — if provided, the worker will POST the job result to this URL on completion

## Async Job Processing

When a task is created, a background notification job is queued via Celery and processed independently of the HTTP request:

- `POST /tasks/` returns immediately with the task data and a `job_id`
- The Celery worker processes the job asynchronously, creates a `Notification` record in the DB, and fires a webhook if `callback_url` was provided
- Poll `GET /tasks/jobs/{job_id}` to check job status (`PENDING`, `STARTED`, `SUCCESS`, `FAILURE`)
- On success, the webhook payload is `{"job_id": ..., "status": "SUCCESS", "user_id": ...}`

This decouples notification delivery from the request cycle — a slow or failing notification never blocks the API response.

## Design Decisions

**1. 404 for both missing and unauthorized tasks**
When a user requests a task they don't own, the API returns 404 instead of 403. Returning 403 would confirm that the task exists, leaking information about other users' data. By always returning 404, the API doesn't reveal anything about resources the requesting user has no access to.

**2. `get_db` uses `try/finally` without `except`**
The dependency only needs to guarantee the session is closed after the request — success or failure. Catching exceptions here would swallow errors before the global exception handler could log and handle them properly. `finally` ensures cleanup without interfering with the error handling chain.

**3. `create_access_token` accepts a `dict` instead of a `User` object**
Keeping the function generic means it has no dependency on the User model. Any part of the system could call it with any payload. This makes it reusable — for example, if refresh tokens with a different payload shape are added later, the same function handles it without changes.

**4. `request_id` attached to every log line**
A middleware generates a UUID per request and binds it to the structlog context. Every log event within that request automatically includes the `request_id`. In production, this makes it possible to trace all log lines belonging to a single request without any extra work at the call site.

**5. Celery worker uses a sync SQLAlchemy session**
Celery tasks run in a separate process with no event loop. Using the async SQLAlchemy session inside a Celery task would require spinning up an event loop manually, which is error-prone. A dedicated sync engine and session factory is used in the worker process only, keeping async strictly in the FastAPI layer.

**6. Cache invalidation on mutation**
`PUT` and `DELETE` on a task immediately delete the Redis cache entry for that task. This ensures the next read always fetches fresh data from the DB. A 300 second TTL is also set on cache entries as a safety net, so stale data can never persist indefinitely even if invalidation fails.

**7. Rate limiting uses `INCR` + conditional `EXPIRE`**
The login rate limiter increments a Redis counter per IP and sets a 60 second expiry only when the counter is first created (i.e. when `INCR` returns 1). Setting expiry on every request would reset the window on each attempt, allowing indefinite retries. Setting it once ensures the window is fixed from the first request.