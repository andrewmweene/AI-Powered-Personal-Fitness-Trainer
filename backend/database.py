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
from sqlalchemy.orm import declarative_base, sessionmaker

# Load environment variables from a .env file in the project root if present
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
dotenv_path = os.path.join(project_root, ".env")
load_dotenv(dotenv_path)
print("dotenv_path:", dotenv_path)
print("dotenv exists:", os.path.exists(dotenv_path))
print("env DATABASE_URL:", os.getenv("DATABASE_URL"))


DATABASE_URL = os.environ.get("DATABASE_URL")
print("DATABASE_URL:", DATABASE_URL)
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set (and not found in .env).")

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)

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
