"""Landing page, login, and registration views for the Streamlit app."""

from __future__ import annotations

import httpx
import streamlit as st


def _get_api_base() -> str:
    return st.session_state.get("api_base", "http://localhost:8000").rstrip("/")


def _login(username: str, password: str) -> bool:
    api_base = _get_api_base()
    try:
        response = httpx.post(
            f"{api_base}/users/login",
            json={"username": username, "password": password},
            timeout=10.0,
        )
        response.raise_for_status()
        token_data = response.json()
        st.session_state.token = token_data.get("access_token")
        st.session_state.user = username
        st.session_state.onboarding_complete = None
        st.session_state.current_page = "Dashboard"
        return True
    except httpx.HTTPStatusError as exc:
        message = exc.response.json().get("detail", "Unable to log in.")
        st.error(message)
    except Exception:
        st.error("Unable to reach the backend. Check your API base URL.")
    return False


def _register(username: str, email: str, password: str, age: int, fitness_level: str, goal: str) -> bool:
    api_base = _get_api_base()
    try:
        response = httpx.post(
            f"{api_base}/users/register",
            json={
                "username": username,
                "email": email,
                "password": password,
                "age": age,
                "fitness_level": fitness_level,
                "goal": goal,
            },
            timeout=10.0,
        )
        response.raise_for_status()
        st.success("Account created successfully. Please sign in.")
        return True
    except httpx.HTTPStatusError as exc:
        message = exc.response.json().get("detail", "Unable to register.")
        st.error(message)
    except Exception:
        st.error("Unable to reach the backend. Check your API base URL.")
    return False


def render() -> None:
    """Render the home page with login and registration options."""
    st.title("AI Personal Trainer")
    st.write("Welcome to your AI-powered fitness coach.")
    st.subheader("Sign in or create an account to begin.")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign In")

        if submitted:
            if not username or not password:
                st.error("Username and password are required.")
            elif _login(username, password):
                st.experimental_rerun()

    with st.form("register_form"):
        st.write("Create a new account")
        username = st.text_input("Username", key="register_username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password", key="register_password")
        confirm_password = st.text_input("Confirm password", type="password", key="confirm_password")
        age = st.number_input("Age", min_value=13, max_value=100, value=18)
        fitness_level = st.selectbox("Fitness level", ["beginner", "intermediate", "advanced"])
        goal = st.selectbox(
            "Fitness goal",
            [
                "weight_loss",
                "muscle_gain",
                "strength_training",
                "endurance",
                "general_fitness",
            ],
        )
        registered = st.form_submit_button("Create Account")

        if registered:
            if password != confirm_password:
                st.error("Passwords do not match.")
            elif not username or not email or not password:
                st.error("All fields are required.")
            elif _register(username, email, password, age, fitness_level, goal):
                st.success("Registration successful. You can now sign in.")

    st.write("Use the navigation menu to start an exercise session or view your dashboard after signing in.")
