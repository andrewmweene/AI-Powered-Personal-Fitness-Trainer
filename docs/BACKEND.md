# Backend

This document outlines the FastAPI backend architecture, data models, authentication flow, and router structure.

- `backend/main.py`: FastAPI app entry point.
- `backend/database.py`: SQLAlchemy engine and session factory.
- `backend/models.py`: ORM models including users, sessions, workout plans, and feedback logs.
- `backend/schemas.py`: Pydantic request and response schemas.
- `backend/auth.py`: password hashing and JWT creation/validation.
- `backend/dependencies.py`: request-scoped dependencies for database sessions and authentication.
- `backend/routers/`: API endpoints for users, sessions, analytics, and recommendations.
