# Task Management API

## What is this?
A production-style RESTful API for managing tasks, built from scratch to learn FastAPI, system design, and backend engineering practices. Users can register, authenticate, and manage their own tasks with full CRUD support.

## Tech Stack
- **Python 3.11**
- **FastAPI** — web framework
- **PostgreSQL** — primary database
- **SQLAlchemy** — ORM and query building
- **Pydantic v2** — request/response validation and settings management
- **passlib + bcrypt** — password hashing
- **python-jose** — JWT encoding and decoding
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
   Fill in `DATABASE_URL`, `SECRET_KEY`, `ALGORITHM`, and `ACCESS_TOKEN_EXPIRE_MINUTES`.

3. Start the services
   ```bash
   docker compose up
   ```

4. Verify the app is running
   ```bash
   curl http://localhost:8080/health
   ```

5. Explore the API via Swagger UI at `http://localhost:8080/docs`

## API Endpoints

| Method | Path | Auth Required | Description |
|--------|------|---------------|-------------|
| GET | `/health` | No | Health check |
| POST | `/auth/register` | No | Register a new user |
| POST | `/auth/login` | No | Login and receive JWT |
| POST | `/tasks/` | Yes | Create a task |
| GET | `/tasks/` | Yes | Get all tasks (paginated, filterable by status) |
| GET | `/tasks/{id}` | Yes | Get a single task |
| PUT | `/tasks/{id}` | Yes | Update a task |
| DELETE | `/tasks/{id}` | Yes | Delete a task |

### Query Parameters for `GET /tasks`
- `page` (default: 1)
- `page_size` (default: 10)
- `status` — filter by task status: `PENDING`, `INPROGRESS`, `COMPLETED`, `CANCELLED`

## Design Decisions

**1. 404 for both missing and unauthorized tasks**
When a user requests a task they don't own, the API returns 404 instead of 403. Returning 403 would confirm that the task exists, leaking information about other users' data. By always returning 404, the API doesn't reveal anything about resources the requesting user has no access to.

**2. `get_db` uses `try/finally` without `except`**
The dependency only needs to guarantee the session is closed after the request — success or failure. Catching exceptions here would swallow errors before the global exception handler could log and handle them properly. `finally` ensures cleanup without interfering with the error handling chain.

**3. `create_access_token` accepts a `dict` instead of a `User` object**
Keeping the function generic means it has no dependency on the User model. Any part of the system could call it with any payload. This makes it reusable — for example, if refresh tokens with a different payload shape are added later, the same function handles it without changes.

**4. `request_id` attached to every log line**
A middleware generates a UUID per request and binds it to the structlog context. Every log event within that request automatically includes the `request_id`. In production, this makes it possible to trace all log lines belonging to a single request without any extra work at the call site.
