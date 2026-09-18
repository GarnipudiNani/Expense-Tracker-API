# Expense Tracker API

A RESTful Expense Tracker API built with **Python and FastAPI** that allows users to securely manage their personal expenses.

The application provides user registration and authentication, expense CRUD operations, filtering by category and date, PostgreSQL database integration, database migrations using Alembic, automated testing with Pytest, and interactive API documentation using Swagger/OpenAPI.

---

## 🚀 Features

- User registration and login
- JWT-based authentication
- User-specific expense management
- Create, read, update, and delete expenses
- Filter expenses by category
- Filter expenses by date range
- Update username
- Delete user account
- PostgreSQL database integration
- Database migrations using Alembic
- Environment variable configuration
- Automated testing using Pytest
- Interactive Swagger/OpenAPI documentation

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| Python | Backend programming |
| FastAPI | REST API framework |
| PostgreSQL | Database |
| SQLAlchemy | Database ORM |
| JWT | Authentication |
| Alembic | Database migrations |
| Pytest | Automated testing |
| Swagger/OpenAPI | API documentation |
| Git & GitHub | Version control |

---

## 🏗️ Application Architecture

```text
                         Client
                           |
                           v
                   FastAPI REST API
                           |
              +------------+------------+
              |                         |
              v                         v
       Authentication            Expense Management
              |                         |
              v                         v
             JWT                  CRUD Operations
                                        |
                                        v
                                 Filtering System
                                  /           \
                                 /             \
                            Category        Date Range
                                 \             /
                                  \           /
                                   v         v
                                    SQLAlchemy
                                        |
                                        v
                                   PostgreSQL
```

---

## 🔐 Authentication

The API uses **JSON Web Tokens (JWT)** for authentication.

### Authentication Flow

```text
User Registration
       |
       v
     Login
       |
       v
JWT Access Token
       |
       v
Authenticated Request
       |
       v
Protected API Endpoint
```

Only authenticated users can access protected expense endpoints.

Users can manage their own expense records through authenticated requests.

---

## 📌 API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/signup` | Register a new user |
| POST | `/login` | Login and obtain JWT token |

### Expenses

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/expenses` | Retrieve user expenses |
| POST | `/expenses` | Create a new expense |
| PUT | `/expenses/{id}` | Update an expense |
| DELETE | `/expenses/{id}` | Delete an expense |

### User Account

| Method | Endpoint | Description |
|--------|----------|-------------|
| PUT | `/user` | Update username |
| DELETE | `/user` | Delete user account |

---

## 🔎 Expense Filtering

The API supports filtering expenses by:

- Category
- Start date
- End date

### Example

```text
GET /expenses?category=Food
```

Date range example:

```text
GET /expenses?start_date=2026-09-01&end_date=2026-09-30
```

This allows users to retrieve specific expense records instead of retrieving their complete expense history.

---

## 🗄️ Database

The application uses **PostgreSQL** for persistent data storage.

Database schema changes are managed using **Alembic migrations**.

Sensitive configuration values such as the database URL and JWT secret key are stored using environment variables.

### Environment Variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://<username>:<password>@localhost/<database>
SECRET_KEY=<your-secret-key>
```

> **Important:** Never commit your `.env` file or expose your secret key in the repository.

---

## 🧪 Testing

The project uses **Pytest** for automated testing.

Run the tests with:

```bash
pytest
```

---

## 📖 API Documentation

FastAPI automatically generates interactive API documentation using Swagger/OpenAPI.

After starting the application, open:

```text
http://localhost:8000/docs
```

Swagger UI allows you to:

- View available endpoints
- Test API requests
- Authenticate using JWT
- Inspect request parameters
- View API responses

---

## ⚙️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/GarnipudiNani/Expense-Tracker-API.git
```

### 2. Navigate to the Project Directory

```bash
cd Expense-Tracker-API
```

### 3. Create a Virtual Environment

#### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

#### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file:

```env
DATABASE_URL=postgresql://<username>:<password>@localhost/<database>
SECRET_KEY=<your-secret-key>
```

Replace the placeholder values with your PostgreSQL credentials and a secure secret key.

### 6. Run Database Migrations

```bash
alembic upgrade head
```

### 7. Start the Application

```bash
uvicorn main:app --reload
```

The API will be available at:

```text
http://localhost:8000
```

### 8. Open Swagger Documentation

Visit:

```text
http://localhost:8000/docs
```

---

## 📂 Project Structure

```text
Expense-Tracker-API/
│
├── app/
│   ├── __init__.py
│   ├── database.py        # SQLAlchemy engine/session, get_db dependency
│   ├── models.py           # User and Expense ORM models
│   ├── schemas.py          # Pydantic request/response schemas
│   ├── security.py         # Password hashing, JWT creation/decoding
│   ├── deps.py              # get_current_user dependency
│   └── routers/
│       ├── auth.py          # /signup, /login
│       ├── expenses.py      # /expenses CRUD + filtering
│       └── users.py         # /user update/delete
│
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── ..._create_users_and_expenses_tables.py
│
├── tests/
│   ├── conftest.py          # Test fixtures (isolated in-memory SQLite DB)
│   ├── test_auth.py
│   ├── test_expenses.py
│   ├── test_authorization.py
│   └── test_user.py
│
├── main.py                  # FastAPI app entrypoint
├── alembic.ini
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## 🔄 Application Workflow

```text
1. User creates an account
          ↓
2. User logs in
          ↓
3. API generates JWT token
          ↓
4. User sends authenticated request
          ↓
5. API validates JWT
          ↓
6. Expense operation is performed
          ↓
7. PostgreSQL stores/retrieves data
          ↓
8. API returns the response
```

---

## 💡 Example Use Case

A user can use the API to:

```text
Register
   ↓
Login
   ↓
Create Expense
   ↓
View Expenses
   ↓
Filter by Category / Date
   ↓
Update Expense
   ↓
Delete Expense
```

Example expense records:

```text
Food        → ₹500
Transport   → ₹200
Shopping    → ₹1,000
Food        → ₹350
```

Users can filter their expenses by category or date range.

---

## 🔒 Security

The project implements basic security practices including:

- JWT-based authentication
- Protected API endpoints
- User-specific data access
- Environment variables for sensitive configuration
- `.gitignore` protection for the `.env` file

For production deployment, additional security measures such as HTTPS, secure secret management, rate limiting, and production server configuration should be considered.

---

## ✅ Verified

Every endpoint and workflow below was exercised end-to-end against a real
PostgreSQL database, plus a 26-test automated Pytest suite (`pytest -q`
→ `26 passed`):

- Signup, duplicate-signup rejection, login, invalid-login rejection
- Missing/invalid JWT rejection on protected routes
- Expense create / list / update / delete
- Category filtering and date-range filtering (including an invalid range → 400)
- Field validation (negative amount, missing field, future date, short password → 422)
- User A cannot view, update, or delete User B's expenses (404, not 403, so ids
  can't be probed)
- Username update, username-conflict rejection, account deletion
- Deleting a user cascades and removes their expenses
- `alembic upgrade head` against a fresh PostgreSQL database
- `/docs` and `/redoc` render correctly

## 🔮 Future Improvements

Possible future improvements include:

- Monthly expense summaries
- Budget management
- Spending analytics
- Pagination and sorting
- Expense statistics
- Docker containerization
- CI/CD pipeline
- Frontend dashboard
- Cloud deployment

---

## 📚 Project Inspiration

This project was developed based on the **Expense Tracker API** project idea from [roadmap.sh](https://roadmap.sh/projects/expense-tracker-api).

The project helped strengthen practical skills in:

- Python backend development
- FastAPI
- REST API design
- PostgreSQL
- JWT authentication
- Database migrations
- Automated testing

---

## 👨‍💻 Author

**Nani Garnipudi**

GitHub: [GarnipudiNani](https://github.com/GarnipudiNani)

---

## ⭐ Feedback

If you find this project useful or have suggestions for improvement, feel free to open an issue or submit a pull request.

If you find the project helpful, consider giving the repository a ⭐.
