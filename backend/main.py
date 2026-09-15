"""FastAPI application entry point for the AI Personal Trainer backend."""

import logging
import os

from fastapi import FastAPI  # type: ignore[reportMissingImports]

environment = os.getenv("ENV", "development").lower()
logging.basicConfig(level=logging.DEBUG if environment == "development" else logging.INFO)
from fastapi.middleware.cors import CORSMiddleware

from .routers import analytics, onboarding, recommendations, sessions, users, pose, measurements
from .database import Base, engine
from .demo import ensure_demo_user


app = FastAPI(title="AI Personal Trainer API", version="1.0.0")

frontend_origins = [
    origin.strip()
    for origin in os.getenv("FRONTEND_ORIGIN", "http://localhost:5173").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=frontend_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users, prefix="/users", tags=["users"])
app.include_router(onboarding, prefix="/onboarding", tags=["onboarding"])
app.include_router(sessions, prefix="/sessions", tags=["sessions"])
app.include_router(analytics, prefix="/analytics", tags=["analytics"])
app.include_router(recommendations, prefix="/recommendations", tags=["recommendations"])
app.include_router(pose, prefix="/pose", tags=["pose"])
app.include_router(measurements, prefix="/measurements", tags=["measurements"])


@app.on_event("startup")
def on_startup() -> None:
    """Ensure database tables are created on application startup (development only)."""
    Base.metadata.create_all(bind=engine)
    ensure_demo_user()


@app.get("/health")
def health_check() -> dict[str, str]:
    """Return a basic health check response."""
    return {"status": "ok"}


@app.get("/")
def root() -> dict[str, str]:
    """Root health endpoint."""
    return {"status": "ok"}
