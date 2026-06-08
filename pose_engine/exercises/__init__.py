"""Exercise definitions for the AI Personal Trainer pose engine."""

from .base_exercise import BaseExercise
from .squat import Squat
from .bicep_curl import BicepCurl
from .pushup import PushUp
from .dumbbell_fly import DumbbellFly
from .kickback import Kickback

__all__ = [
    "BaseExercise",
    "Squat",
    "BicepCurl",
    "PushUp",
    "DumbbellFly",
    "Kickback",
]
