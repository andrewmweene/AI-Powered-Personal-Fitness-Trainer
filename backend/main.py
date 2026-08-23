"""FastAPI application entry point for the AI Personal Trainer backend."""

from fastapi import FastAPI  # type: ignore[reportMissingImports]
import logging

# Enable debug logging for local development to aid troubleshooting.
logging.basicConfig(level=logging.DEBUG)
from fastapi.middleware.cors import CORSMiddleware

from .routers import analytics, onboarding, recommendations, sessions, users, pose
from .database import Base, engine


app = FastAPI(title="AI Personal Trainer API", version="1.0.0")

# CORS (development): allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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


@app.on_event("startup")
def on_startup() -> None:
    """Ensure database tables are created on application startup (development only)."""
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Return a basic health check response."""
    return {"status": "ok"}


@app.get("/")
def root() -> dict[str, str]:
    """Root health endpoint."""
    return {"status": "ok"}
