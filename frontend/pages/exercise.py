"""Live webcam exercise page for capturing posture and rep data."""

from __future__ import annotations

import cv2
import streamlit as st


def render() -> None:
    """Render the exercise page with webcam preview and session controls."""
    st.title("Live Exercise")
    st.write("Use your webcam to track reps, posture accuracy, and live feedback.")
    placeholder = st.empty()
    if st.button("Start Session"):
        cap = cv2.VideoCapture(0)
        rep_counter = 0
        accuracy = 0.0
        feedback = "Ready when you are."
        while cap.isOpened() and rep_counter < 1:
            success, frame = cap.read()
            if not success:
                break
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            placeholder.image(frame, channels="RGB")
            st.write(f"Reps: {rep_counter}")
            st.write(f"Posture accuracy: {accuracy:.1f}%")
            st.write(feedback)
            break
        cap.release()
        st.write("Session complete. Post session data to the backend when available.")
