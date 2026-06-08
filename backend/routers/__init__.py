"""API routers package for the backend application."""

from .analytics import router as analytics
from .recommendations import router as recommendations
from .sessions import router as sessions
from .users import router as users

__all__ = ["analytics", "recommendations", "sessions", "users"]
