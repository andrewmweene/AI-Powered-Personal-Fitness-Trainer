"""Streamlit entry point for the AI Personal Trainer frontend application."""

from __future__ import annotations

import os
import sys

import streamlit as st

# Ensure the repository root is on sys.path so we can import analytics, recommendation, etc.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Also ensure the frontend directory is on sys.path so we can import pages
frontend_root = os.path.dirname(__file__)
if frontend_root not in sys.path:
    sys.path.insert(0, frontend_root)

from pages import dashboard, exercise, home, workout_plan

PAGES = {
    "Home": home,
    "Exercise": exercise,
    "Dashboard": dashboard,
    "Workout Plan": workout_plan,
}


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
    
    st.sidebar.title("AI Personal Trainer")
    
    # Show different navigation based on login state
    if st.session_state.token is None:
        # Only show Home for unauthenticated users
        selection = "Home"
    else:
        # Show all pages for authenticated users
        selection = st.sidebar.radio("Navigate", list(PAGES.keys()))
        if st.sidebar.button("Logout"):
            st.session_state.token = None
            st.session_state.user = None
            st.rerun()
    
    page = PAGES[selection]
    page.render()


if __name__ == "__main__":
    main()
