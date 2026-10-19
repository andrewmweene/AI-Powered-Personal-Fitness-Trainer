"""FastAPI application entry point for the AI Personal Trainer backend."""

from contextlib import asynccontextmanager
import logging
import os

from fastapi import FastAPI  # type: ignore[reportMissingImports]
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

environment = os.getenv("ENV", "development").lower()
logging.basicConfig(level=logging.DEBUG if environment == "development" else logging.INFO)
from fastapi.middleware.cors import CORSMiddleware

from .routers import analytics, onboarding, recommendations, sessions, users, pose, measurements, auth
from .routers.auth import limiter
from .database import Base, engine
from .demo import ensure_demo_user


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables and seed the demo user at startup."""
    Base.metadata.create_all(bind=engine)
    ensure_demo_user()
    yield


app = FastAPI(
    title="AI Personal Trainer API",
    version="1.0.0",
    lifespan=lifespan,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

_origins_raw = (
    os.getenv("ALLOWED_ORIGINS")
    or os.getenv("FRONTEND_ORIGIN")
    or "http://localhost:5173,http://localhost:4173"
)
allowed_origins = [origin.strip() for origin in _origins_raw.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
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
app.include_router(auth, prefix="/auth", tags=["auth"])


@app.get("/health")
def health_check() -> dict[str, str]:
    """Return a basic health check response."""
    return {"status": "ok"}


@app.get("/")
def root() -> dict[str, str]:
    """Root health endpoint."""
    return {"status": "ok"}
