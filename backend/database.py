"""SQLAlchemy database engine and session factory configuration.

This module reads configuration from the environment (via python-dotenv),
creates the SQLAlchemy engine, a `SessionLocal` factory, and exposes a
`get_db()` FastAPI dependency generator.
"""

from __future__ import annotations

from typing import Generator
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

# Load environment variables from a .env file in the project root if present
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
dotenv_path = os.path.join(project_root, ".env")
load_dotenv(dotenv_path)

DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./fitness_trainer.db"


def _build_engine(url: str):
    if url.startswith("sqlite"):
        return create_engine(url)

    try:
        engine = create_engine(url, pool_pre_ping=True)
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return engine
    except Exception:
        return create_engine("sqlite:///./fitness_trainer.db")


# Create the SQLAlchemy engine
engine = _build_engine(DATABASE_URL)

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
