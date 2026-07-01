"""Streamlit onboarding page for collecting user profile details and assigning a workout plan."""

from __future__ import annotations

import httpx
import streamlit as st


def _get_api_base() -> str:
    return st.session_state.get("api_base", "http://localhost:8000").rstrip("/")


def _get_headers() -> dict[str, str]:
    token = st.session_state.get("token")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


def _ensure_state() -> None:
    if "onboarding_step" not in st.session_state:
        st.session_state.onboarding_step = 2
    if "onboarding_data" not in st.session_state:
        st.session_state.onboarding_data = {}


def _calculate_bmi(height_cm: float, weight_kg: float) -> float:
    if height_cm <= 0:
        return 0.0
    return round(weight_kg / ((height_cm / 100) ** 2), 1)


def _bmi_category(bmi: float) -> str:
    if bmi < 18.5:
        return "Underweight"
    if bmi < 25.0:
        return "Normal weight"
    if bmi < 30.0:
        return "Overweight"
    return "Obese"


def _submit_onboarding() -> None:
    api_base = _get_api_base()
    headers = _get_headers()
    if not headers:
        st.error("Authentication required. Please log in again.")
        return

    payload = st.session_state.onboarding_data
    try:
        response = httpx.post(
            f"{api_base}/onboarding/complete",
            json=payload,
            headers=headers,
            timeout=10.0,
        )
        response.raise_for_status()
    except httpx.HTTPStatusError as error:
        detail = error.response.json().get("detail") if error.response is not None else str(error)
        st.error(detail or "Unable to complete onboarding.")
        return
    except Exception as error:
        st.error(f"Unable to connect to the backend: {error}")
        return

    st.session_state.onboarding_complete = True
    st.session_state.current_page = "Dashboard"
    st.experimental_rerun()


def render() -> None:
    """Render the onboarding wizard page."""
    _ensure_state()
    step = int(st.session_state.onboarding_step)
    step_names = {
        2: "Body profile",
        3: "Workout goal",
        4: "Equipment",
        5: "Availability",
    }

    st.progress((step - 1) / 4)
    st.caption(f"Step {step} of 5 — {step_names.get(step, 'Onboarding')}" )
    st.title("Complete Your Onboarding")

    if st.session_state.get("token") is None:
        st.error("You must be logged in to complete onboarding.")
        return

    if step == 2:
        st.header("Tell us about your body")
        data = st.session_state.onboarding_data
        age = st.number_input("Age", min_value=13, max_value=100, value=data.get("age", 25), step=1)
        gender = st.selectbox(
            "Gender (optional)",
            ["", "Male", "Female", "Non-binary", "Prefer not to say"],
            index=0 if data.get("gender") is None else ["", "Male", "Female", "Non-binary", "Prefer not to say"].index(data.get("gender")),
        )
        height_cm = st.number_input("Height (cm)", min_value=50.0, max_value=300.0, value=data.get("height_cm", 170.0), step=0.5)
        weight_kg = st.number_input("Weight (kg)", min_value=20.0, max_value=300.0, value=data.get("weight_kg", 70.0), step=0.5)
        fitness_level = st.radio(
            "Fitness level",
            ["Beginner", "Intermediate", "Advanced"],
            index={"beginner": 0, "intermediate": 1, "advanced": 2}.get(data.get("fitness_level", "beginner"), 0),
        )

        bmi = _calculate_bmi(height_cm, weight_kg)
        st.metric("BMI", f"{bmi:.1f}")
        st.write(f"Category: {_bmi_category(bmi)}")
        st.caption("BMI is shown for reference only and does not affect your workout plan.")

        if st.button("Continue →"):
            st.session_state.onboarding_data.update(
                {
                    "age": int(age),
                    "gender": gender if gender != "" else None,
                    "height_cm": float(height_cm),
                    "weight_kg": float(weight_kg),
                    "fitness_level": fitness_level.lower(),
                }
            )
            st.session_state.onboarding_step = 3
            st.experimental_rerun()

    elif step == 3:
        st.header("Choose your workout goal")
        goal_descriptions = {
            "weight_loss": "Focus on burning calories and improving body composition.",
            "muscle_gain": "Build strength and lean muscle with consistent resistance work.",
            "strength_training": "Increase strength with progressive lifting and compound movement.",
            "endurance": "Improve stamina and conditioning for longer activity.",
            "general_fitness": "Build all-round fitness and healthy movement habits.",
            "flexibility": "Improve mobility and muscle function with balanced training.",
            "sports_specific": "Train with a focus on sport performance and functional strength.",
        }
        selected_goal = st.radio(
            "Goal",
            [
                "weight_loss",
                "muscle_gain",
                "strength_training",
                "endurance",
                "general_fitness",
                "flexibility",
                "sports_specific",
            ],
            index=[
                "weight_loss",
                "muscle_gain",
                "strength_training",
                "endurance",
                "general_fitness",
                "flexibility",
                "sports_specific",
            ].index(st.session_state.onboarding_data.get("goal", "weight_loss")),
        )
        st.caption(goal_descriptions[selected_goal])

        cols = st.columns([1, 1])
        if cols[0].button("← Back"):
            st.session_state.onboarding_step = 2
            st.experimental_rerun()
        if cols[1].button("Continue →"):
            st.session_state.onboarding_data["goal"] = selected_goal
            st.session_state.onboarding_step = 4
            st.experimental_rerun()

    elif step == 4:
        st.header("What equipment can you use?")
        equipment_choice = st.radio(
            "I have equipment or bodyweight only",
            ["I have equipment", "Bodyweight only"],
            index=0 if st.session_state.onboarding_data.get("has_equipment", False) else 1,
        )
        has_equipment = equipment_choice == "I have equipment"
        equipment_list = st.session_state.onboarding_data.get("equipment_list", [])
        if has_equipment:
            equipment_list = st.multiselect(
                "Select available equipment",
                [
                    "Dumbbells",
                    "Resistance bands",
                    "Pull-up bar",
                    "Kettlebell",
                    "Barbell + rack",
                    "Bench",
                    "Cables/machine",
                    "Full gym access",
                ],
                default=equipment_list,
            )

        cols = st.columns([1, 1])
        if cols[0].button("← Back"):
            st.session_state.onboarding_step = 3
            st.experimental_rerun()
        if cols[1].button("Continue →"):
            if has_equipment and not equipment_list:
                st.error("Please select at least one piece of equipment or switch to bodyweight only.")
            else:
                st.session_state.onboarding_data["has_equipment"] = has_equipment
                st.session_state.onboarding_data["equipment_list"] = equipment_list if has_equipment else []
                st.session_state.onboarding_step = 5
                st.experimental_rerun()

    elif step == 5:
        st.header("Set your availability")
        data = st.session_state.onboarding_data
        days_per_week = st.slider("Days per week", min_value=1, max_value=7, value=data.get("days_per_week", 3))
        workout_duration_minutes = st.selectbox(
            "Workout duration (minutes)",
            [15, 20, 30, 45, 60, 75, 90],
            index=[15, 20, 30, 45, 60, 75, 90].index(data.get("workout_duration_minutes", 30)),
        )
        preferred_time = st.selectbox(
            "Preferred time",
            [
                "Early morning (5–8 am)",
                "Morning (8–11 am)",
                "Midday (11 am–2 pm)",
                "Afternoon (2–5 pm)",
                "Evening (5–8 pm)",
                "Late evening (8–11 pm)",
            ],
            index=[
                "Early morning (5–8 am)",
                "Morning (8–11 am)",
                "Midday (11 am–2 pm)",
                "Afternoon (2–5 pm)",
                "Evening (5–8 pm)",
                "Late evening (8–11 pm)",
            ].index(data.get("preferred_time", "Morning (8–11 am)")),
        )

        st.session_state.onboarding_data.update(
            {
                "days_per_week": int(days_per_week),
                "workout_duration_minutes": int(workout_duration_minutes),
                "preferred_time": preferred_time,
            }
        )

        st.subheader("Here is your profile summary — please confirm before we build your plan.")
        summary_left, summary_right = st.columns(2)
        summary_left.metric("Age", data.get("age", "—"))
        summary_left.metric("Height (cm)", data.get("height_cm", "—"))
        summary_left.metric("Weight (kg)", data.get("weight_kg", "—"))
        summary_left.metric("Fitness level", data.get("fitness_level", "—").title())
        summary_right.metric("Goal", data.get("goal", "—").replace("_", " ").title())
        summary_right.metric("Days / week", data.get("days_per_week", "—"))
        summary_right.metric("Duration", f"{data.get('workout_duration_minutes', '—')} min")
        summary_right.metric("Preferred time", data.get("preferred_time", "—"))
        if data.get("has_equipment"):
            summary_right.write("Equipment: " + ", ".join(data.get("equipment_list", [])) or "None")
        else:
            summary_right.write("Equipment: Bodyweight only")

        cols = st.columns([1, 1])
        if cols[0].button("← Back"):
            st.session_state.onboarding_step = 4
            st.experimental_rerun()
        if cols[1].button("Build my plan →"):
            _submit_onboarding()

    else:
        st.write("Invalid onboarding step.")
