# Expense Tracker API

[![CI](https://github.com/GarnipudiNani/Expense-Tracker-API/actions/workflows/ci.yml/badge.svg)](https://github.com/GarnipudiNani/Expense-Tracker-API/actions/workflows/ci.yml)

A FastAPI backend for securely tracking personal expenses with JWT authentication and PostgreSQL persistence.

Live demo: `<LIVE_DEMO_URL>`

Screenshot: `<SCREENSHOT_URL_OR_IMAGE_PATH>`

Features:
- Register and authenticate users with bearer tokens.
- Create, list, filter, update, and delete personal expenses.
- Summarize expense totals and counts by category.
- Manage the database schema with Alembic migrations.

## Quick start with Docker

Docker Compose starts the API and PostgreSQL. The API waits for the database health check, applies migrations, and then serves the application.

```bash
docker compose up
```

Open [http://localhost:8000/docs](http://localhost:8000/docs) for the interactive API documentation. The bundled Compose defaults are for local development only. Copy `.env.example` to `.env` to customize them; replace development placeholders before using any configuration outside local development.

## Local setup

Requires Python 3.12+ and PostgreSQL. From the repository root:

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

Configure `DATABASE_URL` and `SECRET_KEY` in `.env` or your shell. `.env.example` contains local-development placeholders; do not commit real credentials. Generate a secret with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Apply migrations and start the API:

```bash
alembic upgrade head
uvicorn main:app --reload
```

The API runs at `http://127.0.0.1:8000`; Swagger UI is at `/docs`, ReDoc at `/redoc`, and health checks are at `/health`.

## Features and stack

- Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2, PostgreSQL, Alembic
- JWT bearer authentication and bcrypt password hashing
- Signup, login, username update, and account deletion
- Expense CRUD, category/date filtering, and offset pagination
- Pytest suite using SQLite locally and PostgreSQL in CI

## API

| Method | Path | Purpose | Authentication |
| --- | --- | --- | --- |
| POST | `/signup` | Create an account | No |
| POST | `/login` | Exchange form credentials for a token | No |
| GET | `/expenses` | List, filter, and paginate the current user's expenses | Bearer token |
| GET | `/expenses/summary` | Summarize the current user's expenses by category | Bearer token |
| POST | `/expenses` | Create an expense | Bearer token |
| PUT | `/expenses/{expense_id}` | Partially update an owned expense | Bearer token |
| DELETE | `/expenses/{expense_id}` | Delete an owned expense | Bearer token |
| PUT | `/user` | Change the current username | Bearer token |
| DELETE | `/user` | Delete the current account and its expenses | Bearer token |
| GET | `/health` | Health check | No |

`GET /expenses` accepts `category`, `start_date`, `end_date`, `skip` (default 0, minimum 0), and `limit` (default 10, range 1–100). Date filters are inclusive; results are ordered by date descending and belong only to the current user.

`GET /expenses/summary` accepts optional inclusive `start_date` and `end_date` query parameters. It returns category groups ordered by total descending, then category ascending. For example:

```http
GET /expenses/summary?start_date=2026-09-01&end_date=2026-09-30
Authorization: Bearer <ACCESS_TOKEN>
```

```json
[
  {"category": "Food", "total": "125.50", "count": 4},
  {"category": "Transport", "total": "36.00", "count": 3}
]
```

An invalid date range where `start_date` is after `end_date` returns 400 with `{"detail":"start_date cannot be after end_date"}`. Missing or invalid authentication returns 401. Missing or inaccessible expense IDs return 404. Request validation errors return 422.

## Authentication example

Register:

```bash
curl -X POST http://127.0.0.1:8000/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"sam","password":"a-long-password"}'
```

Login uses URL-encoded form data:

```bash
curl -X POST http://127.0.0.1:8000/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d 'username=sam&password=a-long-password'
```

The response contains `{"access_token":"…","token_type":"bearer"}`. In Swagger, click **Authorize** and enter the token. Example expense request:

```bash
curl -X POST http://127.0.0.1:8000/expenses \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"description":"Lunch","amount":12.50,"category":"Food","date":"2026-11-09"}'
```

Expense amounts must be positive with at most two decimal places. Descriptions and categories must be nonblank and within their field limits; expense dates cannot be in the future. Partial updates require at least one supplied, non-null field.

## Design decisions

- **Per-user data scoping:** Expense reads, updates, deletes, and summaries are scoped to the authenticated user. Another user's expense ID returns 404 rather than 403 so the API does not reveal whether that ID exists.
- **Authentication and passwords:** Protected routes use JWT bearer tokens. Passwords are hashed with bcrypt and are never returned by the API.
- **Validation:** Pydantic validates request fields, including username and text lengths, positive amounts with at most two decimal places, nonblank descriptions/categories, non-null partial updates, and expense dates that are not in the future.
- **Schema management:** Alembic manages database changes; the repository currently has a single baseline migration.
- **Testing:** Tests use a fresh in-memory SQLite database by default. CI sets `TEST_DATABASE_URL` to PostgreSQL so the suite runs against PostgreSQL as well.

## Database migrations

```bash
alembic upgrade head       # apply migrations
alembic current            # show database revision
alembic history            # list revisions
alembic check              # compare models with the current migration
```

Alembic reads `DATABASE_URL` from the environment. The existing baseline migration creates the current schema; no additional migration is required for the expense summary endpoint.

## Tests

Install the development dependencies and run:

```bash
python -m pip install -r requirements-dev.txt
pytest -q
```

Without `TEST_DATABASE_URL`, tests use an isolated in-memory SQLite database. Set `TEST_DATABASE_URL` to a PostgreSQL connection string to run them against PostgreSQL. CI applies migrations and runs the suite against PostgreSQL 16.

## Known limitations

- The schema history consists of a single baseline migration.
- Refresh tokens are not implemented.
- Rate limiting is not implemented.
- No CORS configuration is provided.
- Expense listing uses offset pagination only.

## Project structure

```text
app/                 API schemas, ORM models, security, database and routers
app/routers/         Authentication, expense and user endpoints
alembic/             Database migration environment and revisions
tests/               API and authorization tests
.github/workflows/   GitHub Actions CI
main.py              FastAPI application
requirements.txt     Runtime dependencies
requirements-dev.txt Development and test dependencies
Dockerfile           API container image
docker-compose.yml   Local API and PostgreSQL services
```

## Render deployment

1. Create a Render PostgreSQL database and a Python web service connected to this repository.
2. Set the service build command to `pip install -r requirements.txt`.
3. Set the start command to `uvicorn main:app --host 0.0.0.0 --port $PORT`.
4. Add `DATABASE_URL` using the Render database's internal connection URL and add a strong random `SECRET_KEY`. Optionally set `ACCESS_TOKEN_EXPIRE_MINUTES`.
5. Run `alembic upgrade head` as a pre-deploy command if available in the service plan, or as a release command. Confirm migrations finish before serving new code.
6. Configure any required browser origin restrictions before enabling CORS. This API does not currently enable CORS.
7. Verify `/health` and `/docs` after deployment. Keep secrets in Render environment settings.

The application has no hard-coded production credentials. HTTPS termination and secret management should be provided by the hosting environment.
