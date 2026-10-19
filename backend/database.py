"""SQLAlchemy database engine and session factory configuration.

This module reads configuration from the environment (via python-dotenv),
creates the SQLAlchemy engine, a `SessionLocal` factory, and exposes a
`get_db()` FastAPI dependency generator.
"""

from __future__ import annotations

from typing import Generator
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import declarative_base, sessionmaker


def _normalize_database_url(database_url: str) -> str:
    """Use the installed psycopg2 driver for PostgreSQL connection URLs."""
    url = make_url(database_url)
    if url.drivername in {"postgres", "postgresql", "postgresql+psycopg"}:
        url = url.set(drivername="postgresql+psycopg2")
    return url.render_as_string(hide_password=False)


# Load environment variables from a .env file in the project root if present
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
dotenv_path = os.path.join(project_root, ".env")
load_dotenv(dotenv_path)

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not set. "
        "Copy .env.example to .env and fill in your Supabase connection string."
    )
DATABASE_URL = _normalize_database_url(DATABASE_URL)

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
connect_args = {}
if ENVIRONMENT == "production" and "supabase" in DATABASE_URL:
    connect_args = {"sslmode": "require"}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=False,
)

# Session factory used by application code
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative models
Base = declarative_base()


def get_db() -> Generator:
	"""FastAPI dependency that yields a database session and ensures it is closed.

	Usage in FastAPI endpoints:
		db: Session = Depends(get_db)
	"""
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()
