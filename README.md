Expense Tracker API

CI

A FastAPI backend for securely tracking personal expenses, with JWT authentication, per-user data isolation and PostgreSQL persistence.

Live demo: https://expense-tracker-api-xg7p.onrender.com/docs

Demo project on free hosting: the first request after inactivity can take up to a minute. Please don't enter real personal data.

Features
Register and authenticate users with JWT bearer tokens
Create, list, filter, update and delete personal expenses
Filter by category and date range, with database-level pagination
Summarize expense totals and counts by category (SQL GROUP BY)
Update the username or delete the account together with its expenses
Database schema managed with Alembic migrations
Interactive API documentation at /docs
Tech stack
Python 3.12, FastAPI, Pydantic v2
SQLAlchemy 2, PostgreSQL, Alembic
JWT bearer authentication (python-jose) and bcrypt password hashing
Pytest, with GitHub Actions CI running against PostgreSQL 16
Local setup

Requires Python 3.12+ and PostgreSQL. From the repository root:

bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements-dev.txt

Create a PostgreSQL database, then set DATABASE_URL and SECRET_KEY in a .env file or your shell. .env.example shows the variables; never commit real credentials. Generate a secret with:

bash
python -c "import secrets; print(secrets.token_urlsafe(48))"

The app refuses to start if DATABASE_URL or SECRET_KEY is missing.

Apply migrations and start the API:

bash
alembic upgrade head
uvicorn main:app --reload

The API runs at http://127.0.0.1:8000. Swagger UI is at /docs, ReDoc at /redoc, and the health check at /health.

API
Method	Path	Purpose	Authentication
POST	/signup	Create an account	No
POST	/login	Exchange form credentials for a token	No
GET	/expenses	List, filter and paginate the current user's expenses	Bearer token
GET	/expenses/summary	Summarize the current user's expenses by category	Bearer token
POST	/expenses	Create an expense	Bearer token
PUT	/expenses/{expense_id}	Partially update an owned expense	Bearer token
DELETE	/expenses/{expense_id}	Delete an owned expense	Bearer token
PUT	/user	Change the current username	Bearer token
DELETE	/user	Delete the current account and its expenses	Bearer token
GET	/health	Health check	No

GET /expenses accepts category, start_date, end_date, skip (default 0, minimum 0) and limit (default 10, range 1–100). Date filters are inclusive. Results are ordered by date, newest first, and belong only to the current user.

GET /expenses/summary accepts optional inclusive start_date and end_date query parameters. It returns one entry per category, ordered by total descending and then by category name. Example:

http
GET /expenses/summary?start_date=2026-09-01&end_date=2026-09-30
Authorization: Bearer <ACCESS_TOKEN>
json
[
  {"category": "Food", "total": "125.50", "count": 4},
  {"category": "Transport", "total": "36.00", "count": 3}
]

Status codes: an invalid date range (start_date after end_date) returns 400; missing or invalid authentication returns 401; missing or inaccessible expense IDs return 404; request validation errors return 422.

Authentication example

Register:

bash
curl -X POST http://127.0.0.1:8000/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"sam","password":"a-long-password"}'

Log in (URL-encoded form data):

bash
curl -X POST http://127.0.0.1:8000/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d 'username=sam&password=a-long-password'

The response contains {"access_token":"…","token_type":"bearer"}. In Swagger, click Authorize and enter your username and password. With curl, pass the token as a header:

bash
curl -X POST http://127.0.0.1:8000/expenses \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"description":"Lunch","amount":12.50,"category":"Food","date":"2026-11-09"}'

Expense amounts must be positive with at most two decimal places. Descriptions and categories must be non-blank and within their length limits. Expense dates cannot be in the future. Partial updates require at least one supplied, non-null field.

Design decisions
Per-user data scoping: expense reads, updates, deletes and summaries are all scoped to the authenticated user. Another user's expense ID returns 404 instead of 403, so the API does not reveal whether that ID exists.
Authentication and passwords: protected routes use JWT bearer tokens. Passwords are hashed with bcrypt and never returned by the API.
Validation: Pydantic validates request fields, including text lengths, positive amounts with at most two decimal places, non-blank descriptions and categories, non-null partial updates, and dates that are not in the future.
Schema management: Alembic manages database changes. The repository currently has a single baseline migration.
Testing: tests run on a fresh in-memory SQLite database by default. CI sets TEST_DATABASE_URL to PostgreSQL 16, so the full suite also runs against PostgreSQL.
Database migrations
bash
alembic upgrade head       # apply migrations
alembic current            # show the database revision
alembic history            # list revisions
alembic check              # check that the models match the migrations

Alembic reads DATABASE_URL from the environment.

Tests
bash
python -m pip install -r requirements-dev.txt
pytest -q

Without TEST_DATABASE_URL, tests use an isolated in-memory SQLite database and need no PostgreSQL. To run them against PostgreSQL, set TEST_DATABASE_URL to a PostgreSQL connection string. GitHub Actions applies the migrations and runs the suite against PostgreSQL 16 on every pull request.

Known limitations
The schema history consists of a single baseline migration.
Refresh tokens are not implemented.
Rate limiting is not implemented.
CORS is not configured.
Expense listing uses offset pagination only.
Project structure
text
app/                 API schemas, ORM models, security, database and routers
app/routers/         Authentication, expense and user endpoints
alembic/             Database migration environment and revisions
tests/               API and authorization tests
.github/workflows/   GitHub Actions CI
main.py              FastAPI application
requirements.txt     Runtime dependencies
requirements-dev.txt Development and test dependencies
Render deployment
Create a Render PostgreSQL database and a Python web service connected to this repository.
Set the build command to pip install -r requirements.txt.
Set the start command to uvicorn main:app --host 0.0.0.0 --port $PORT.
Add DATABASE_URL using the Render database's internal connection URL, and add a strong random SECRET_KEY. Optionally set ACCESS_TOKEN_EXPIRE_MINUTES.
Apply migrations with alembic upgrade head. Use Render's pre-deploy command if your plan offers it; otherwise run it once from your machine with DATABASE_URL set to the database's external connection URL. Confirm it finishes before using the API.
Verify /health and /docs after deployment. Keep secrets in Render's environment settings.

The application has no hard-coded production credentials. HTTPS and secret management are provided by the hosting environment.
