"""
Database configuration.

Reads DATABASE_URL from the environment (see .env.example) and exposes:
- engine: the SQLAlchemy engine
- SessionLocal: a session factory
- Base: the declarative base all models inherit from
- get_db: a FastAPI dependency that yields a request-scoped session
"""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL environment variable is not set. "
        "Copy .env.example to .env and fill in your database credentials."
    )

# SQLite (used for local testing) needs this extra connect_arg;
# PostgreSQL (used for the real app) does not.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency: yields a database session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
