# Recommendation

This document explains the recommendation engine for difficulty assessment and plan generation.

- `recommendation/engine.py`: orchestrates rule-based and LLM plan generation.
- `recommendation/rule_based.py`: trains a simple decision tree on synthetic metrics.
- `recommendation/llm_planner.py`: calls Gemini and falls back to rule-based planning.
- `recommendation/schemas.py`: pydantic models for exercises and workout plans.
