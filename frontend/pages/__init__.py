"""Frontend page package for Streamlit page modules."""

from .home import render as render_home
from .exercise import render as render_exercise
from .dashboard import render as render_dashboard
from .workout_plan import render as render_workout_plan

__all__ = ["render_home", "render_exercise", "render_dashboard", "render_workout_plan"]
