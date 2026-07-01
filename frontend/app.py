"""Streamlit entry point for the AI Personal Trainer frontend application."""

from __future__ import annotations

import os
import sys

import httpx
import streamlit as st

# Ensure the repository root is on sys.path so we can import analytics, recommendation, etc.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Also ensure the frontend directory is on sys.path so we can import pages
frontend_root = os.path.dirname(__file__)
if frontend_root not in sys.path:
    sys.path.insert(0, frontend_root)

from pages import dashboard, exercise, home, onboarding, workout_plan

PAGES = {
    "Home": home,
    "Exercise": exercise,
    "Dashboard": dashboard,
    "Workout Plan": workout_plan,
    "Onboarding": onboarding,
}


def _fetch_onboarding_status() -> None:
    api_base = st.session_state.api_base.rstrip("/")
    token = st.session_state.get("token")
    if not token:
        st.session_state.onboarding_complete = False
        return

    try:
        response = httpx.get(
            f"{api_base}/onboarding/status",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10.0,
        )
        response.raise_for_status()
        st.session_state.onboarding_complete = response.json().get("onboarding_complete", False)
    except Exception:
        st.session_state.onboarding_complete = False


def main() -> None:
    """Render the multipage Streamlit application."""
    st.set_page_config(page_title="AI Personal Trainer", layout="wide", initial_sidebar_state="expanded")

    # Initialize session state
    if "token" not in st.session_state:
        st.session_state.token = None
    if "user" not in st.session_state:
        st.session_state.user = None
    if "api_base" not in st.session_state:
        st.session_state.api_base = "http://localhost:8000"
    if "onboarding_complete" not in st.session_state:
        st.session_state.onboarding_complete = None
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Dashboard"

    st.sidebar.title("AI Personal Trainer")

    if st.session_state.token is None:
        selection = "Home"
    else:
        if st.session_state.onboarding_complete is None:
            _fetch_onboarding_status()

        if st.sidebar.button("Logout"):
            st.session_state.token = None
            st.session_state.user = None
            st.session_state.onboarding_complete = None
            st.experimental_rerun()

        if not st.session_state.onboarding_complete:
            selection = "Onboarding"
        else:
            navigation_options = ["Dashboard", "Exercise", "Workout Plan"]
            selection = st.sidebar.radio(
                "Navigate",
                navigation_options,
                index=navigation_options.index(st.session_state.current_page)
                if st.session_state.current_page in navigation_options
                else 0,
            )
            st.session_state.current_page = selection

    page = PAGES[selection]
    page.render()


if __name__ == "__main__":
    main()
