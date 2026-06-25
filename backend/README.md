# Backend - AI Business Opportunity Consultant

FastAPI + SQLAlchemy + Alembic service. Phase 1, Epic 1 delivers Opportunity
management (model, persistence, CRUD endpoints). The LangGraph interview engine,
context graph, scoring and recommendation layers land in later slices.

## Stack

- Python 3.12+, managed with `uv`
- FastAPI (HTTP), Pydantic v2 (schemas/settings)
- SQLAlchemy 2.0 ORM + Alembic migrations
- Postgres 16 (via docker-compose); SQLite in-memory for the test suite

## Layout

```text
backend/
  app/
    api/        # routers (HTTP layer)
    crud/       # persistence operations
    db/         # engine, session, declarative base, portable column types
    models/     # SQLAlchemy ORM models
    schemas/    # Pydantic request/response contracts
    config.py   # settings (env-driven)
    main.py     # app factory + /health
  alembic/      # migration environment + versions
  tests/        # pytest suite (no running DB required)
```

## Getting started

```bash
# 1. Install dependencies (creates .venv)
cd backend
uv sync

# 2. Start Postgres
docker compose -f ../docker-compose.yml up -d db

# 3. Configure environment
cp .env.example .env

# 4. Apply migrations
uv run alembic upgrade head

# 5. Run the API
uv run uvicorn app.main:app --reload
```

Then open http://localhost:8000/docs for the interactive API.

## Common commands

```bash
uv run pytest                 # run the test suite (uses in-memory SQLite)
uv run ruff check .           # lint
uv run ruff format .          # format
uv run mypy app               # type-check
uv run alembic revision --autogenerate -m "message"   # new migration
uv run alembic upgrade head   # apply migrations
```

## API (Epic 1)

| Method | Path                      | Purpose                         |
| ------ | ------------------------- | ------------------------------- |
| GET    | `/health`                 | Liveness probe                  |
| POST   | `/opportunities`          | Create an opportunity (DRAFT)   |
| GET    | `/opportunities`          | List opportunities             |
| GET    | `/opportunities/{id}`     | Fetch one opportunity           |
| PATCH  | `/opportunities/{id}`     | Partial update                  |
| DELETE | `/opportunities/{id}`     | Delete an opportunity           |
