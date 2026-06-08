"""Landing page, login, and registration views for the Streamlit app."""

from __future__ import annotations

import streamlit as st


def render() -> None:
    """Render the home page with login and registration options."""
    st.title("AI Personal Trainer")
    st.write("Welcome to your AI-powered fitness coach.")
    st.subheader("Sign in or create an account to begin.")
    with st.expander("Login"):
        st.text_input("Username")
        st.text_input("Password", type="password")
        st.button("Sign In")
    with st.expander("Register"):
        st.text_input("Email")
        st.text_input("Create password", type="password")
        st.button("Register")
    st.write("Use the navigation menu to start an exercise session or view your dashboard.")
