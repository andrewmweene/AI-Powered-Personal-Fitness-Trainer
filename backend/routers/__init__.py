"""API routers package for the backend application."""

from .analytics import router as analytics
from .onboarding import router as onboarding
from .recommendations import router as recommendations
from .sessions import router as sessions
from .users import router as users
from .pose import router as pose
from .measurements import router as measurements

__all__ = ["analytics", "onboarding", "recommendations", "sessions", "users", "pose", "measurements"]
