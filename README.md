# Expense Tracker API

[![CI](https://github.com/GarnipudiNani/Expense-Tracker-API/actions/workflows/ci.yml/badge.svg)](https://github.com/GarnipudiNani/Expense-Tracker-API/actions/workflows/ci.yml)

A FastAPI backend for personal expense tracking. It provides JWT authentication, user scoped expense CRUD, filtering, pagination, PostgreSQL persistence, and Alembic migrations.

## Features and stack

- Python, FastAPI, Pydantic v2, SQLAlchemy 2, PostgreSQL, Alembic
- JWT bearer authentication and bcrypt password hashing
- Signup, login, username update, and account deletion
- Expense creation, listing, partial updates, and deletion
- Category/date filtering and database level pagination
- Pytest suite using an isolated in memory SQLite database

## Project structure

```text
app/                 API schemas, ORM models, security, database and routers
app/routers/         Authentication, expense and user endpoints
alembic/             Database migration environment and revisions
tests/               API and authorization tests
main.py              FastAPI application
requirements.txt     Runtime dependencies
requirements-dev.txt Development and test dependencies
```

## Local setup

Requires Python 3.10+ and PostgreSQL. From the repository root:

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

Create a PostgreSQL database and configure environment variables in `.env` (or your shell/hosting provider). Never commit real credentials:

```env
DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/DATABASE
SECRET_KEY=replace-with-a-long-random-secret
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Generate a secret with `python -c "import secrets; print(secrets.token_urlsafe(48))"`. Keep the database URL and secret in environment variables in deployment. The app fails at import if required configuration is missing.

Apply migrations and start the local server:

```bash
alembic upgrade head
uvicorn main:app --reload
```

The API runs at `http://127.0.0.1:8000`; Swagger UI is at `/docs`, ReDoc at `/redoc`, and health checks are at `/health`.

## API

| Method | Path | Purpose | Authentication |
| --- | --- | --- | --- |
| POST | `/signup` | Create account (JSON username/password) | No |
| POST | `/login` | Exchange form username/password for a token | No |
| GET | `/expenses` | List/filter/page through your expenses | Bearer token |
| POST | `/expenses` | Create an expense | Bearer token |
| PUT | `/expenses/{expense_id}` | Partially update an expense | Bearer token |
| DELETE | `/expenses/{expense_id}` | Delete an expense | Bearer token |
| PUT | `/user` | Change current username | Bearer token |
| DELETE | `/user` | Delete current account and expenses | Bearer token |

`GET /expenses` accepts `category`, `start_date`, `end_date`, `skip` (default 0, minimum 0), and `limit` (default 10, range 1–100). Date bounds are inclusive. Results belong only to the current user. Invalid date ranges return 400; validation errors return 422; missing/invalid authentication returns 401; unavailable or inaccessible expense IDs return 404.

## Authentication example

Register:

```bash
curl -X POST http://127.0.0.1:8000/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"sam","password":"a-long-password"}'
```

Login uses URL encoded form data:

```bash
curl -X POST http://127.0.0.1:8000/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d 'username=sam&password=a-long-password'
```

The response contains `{"access_token":"…","token_type":"bearer"}`. In Swagger, click **Authorize** and enter the token. Example expense request:

```bash
curl -X POST http://127.0.0.1:8000/expenses \
  -H "Authorization: Bearer YOUR_TOKEN" -H "Content-Type: application/json" \
  -d '{"description":"Lunch","amount":12.50,"category":"Food","date":"2026-11-09"}'
```

Expense amounts must be positive with at most two decimal places; descriptions/categories must be nonblank and fit their field limits; dates cannot be in the future. Partial updates require at least one supplied, non-null field.

## Database migrations

```bash
alembic upgrade head       # apply migrations
alembic current            # show database revision
alembic history            # list revisions
```

Alembic reads `DATABASE_URL` from the environment. No schema changes beyond the existing baseline migration are currently required.

## Tests

```bash
pytest -q
```

Tests override the application database with a fresh in-memory SQLite database and do not require PostgreSQL. JWT configuration is set to a test-only value by the test fixtures. Install `requirements-dev.txt` to run tests; production installs need only `requirements.txt`.

## Render deployment

1. Create a Render PostgreSQL database and a Python web service connected to this repository.
2. Set the service build command to `pip install -r requirements.txt`.
3. Set the start command to `uvicorn main:app --host 0.0.0.0 --port $PORT`.
4. Add `DATABASE_URL` using the Render database's internal connection URL and add a strong random `SECRET_KEY`. Optionally set `ACCESS_TOKEN_EXPIRE_MINUTES`.
5. Run `alembic upgrade head` as a pre-deploy command if available in the service plan, or as a release command. Confirm migrations finish before serving new code.
6. Configure any required browser origin restrictions before enabling CORS. This API does not currently enable permissive CORS; avoid allowing all origins with credentials.
7. Verify `/health` and `/docs` after deployment. Keep secrets in Render environment settings and rotate them through that settings panel.

The application has no hard coded production credentials. HTTPS termination and secret management should be provided by the hosting environment.
