"""Static library of pre-built weekly workout plans for onboarding matching."""

from __future__ import annotations

from typing import Any


def _exercise(exercise: str, sets: int, reps: int, notes: str) -> dict[str, Any]:
    return {
        "exercise": exercise,
        "sets": sets,
        "reps": reps,
        "notes": notes,
    }


def _rest_day() -> dict[str, Any]:
    return {"is_rest": True, "exercises": []}


def _workout_day(exercises: list[dict[str, Any]]) -> dict[str, Any]:
    return {"is_rest": False, "exercises": exercises}


def _build_plan(
    key: str,
    difficulty: str,
    notes: str,
    monday: dict[str, Any],
    tuesday: dict[str, Any],
    wednesday: dict[str, Any],
    thursday: dict[str, Any],
    friday: dict[str, Any],
    saturday: dict[str, Any],
    sunday: dict[str, Any],
) -> dict[str, Any]:
    return {
        "monday": monday,
        "tuesday": tuesday,
        "wednesday": wednesday,
        "thursday": thursday,
        "friday": friday,
        "saturday": saturday,
        "sunday": sunday,
        "difficulty": difficulty,
        "notes": notes,
        "generated_by": "static_library",
        "match_key": key,
    }


PLAN_LIBRARY: dict[str, dict[str, Any]] = {
    "beginner__weight_loss__no_equipment__3d__30min": _build_plan(
        "beginner__weight_loss__no_equipment__3d__30min",
        difficulty="beginner",
        notes="This beginner weight loss plan uses bodyweight conditioning and steady progress with rest days to protect recovery.",
        monday=_workout_day([
            _exercise("Squat", 3, 12, "Drive through your heels and keep your chest up."),
            _exercise("Push-up", 3, 10, "Keep your core tight and lower in a controlled motion."),
        ]),
        tuesday=_rest_day(),
        wednesday=_workout_day([
            _exercise("Squat", 3, 10, "Sit back into the hips with every rep."),
            _exercise("Push-up", 3, 12, "Keep shoulders away from ears and engage your core."),
        ]),
        thursday=_rest_day(),
        friday=_workout_day([
            _exercise("Squat", 3, 12, "Press through your heels to stand tall."),
            _exercise("Push-up", 3, 10, "Keep your spine neutral and your body aligned."),
        ]),
        saturday=_rest_day(),
        sunday=_rest_day(),
    ),
    "beginner__weight_loss__equipment__3d__30min": _build_plan(
        "beginner__weight_loss__equipment__3d__30min",
        difficulty="beginner",
        notes="A beginner equipment plan that blends strength and tempo work for fat loss while building movement quality.",
        monday=_workout_day([
            _exercise("Squat", 3, 10, "Keep weight in your heels and maintain a proud chest."),
            _exercise("Push-up", 3, 10, "Move with control and breathe steadily."),
        ]),
        tuesday=_rest_day(),
        wednesday=_workout_day([
            _exercise("Dumbbell Fly", 3, 12, "Pinch shoulder blades together to protect the shoulder joint."),
            _exercise("Bicep Curl", 3, 12, "Keep elbows pinned to your sides for strict form."),
        ]),
        thursday=_rest_day(),
        friday=_workout_day([
            _exercise("Dumbbell Kickback", 3, 12, "Keep your elbow up and move the weight with your triceps."),
            _exercise("Push-up", 3, 12, "Keep your body in a straight line from head to heels."),
        ]),
        saturday=_rest_day(),
        sunday=_rest_day(),
    ),
    "beginner__muscle_gain__equipment__3d__45min": _build_plan(
        "beginner__muscle_gain__equipment__3d__45min",
        difficulty="beginner",
        notes="This plan builds beginner strength with focused compound movements and recovery between sessions.",
        monday=_workout_day([
            _exercise("Squat", 3, 10, "Keep your knees tracking over your toes."),
            _exercise("Dumbbell Fly", 3, 12, "Keep a slight bend in your elbows and squeeze at the top."),
            _exercise("Bicep Curl", 3, 12, "Control the descent and keep the wrist neutral."),
        ]),
        tuesday=_rest_day(),
        wednesday=_workout_day([
            _exercise("Push-up", 3, 12, "Keep your core braced through every rep."),
            _exercise("Squat", 3, 10, "Drive through heels and breathe out on the way up."),
            _exercise("Dumbbell Kickback", 3, 12, "Keep your elbow still and extend fully."),
        ]),
        thursday=_rest_day(),
        friday=_workout_day([
            _exercise("Squat", 3, 10, "Keep the movement steady and controlled."),
            _exercise("Dumbbell Fly", 3, 12, "Maintain tension in the chest throughout the set."),
            _exercise("Bicep Curl", 3, 12, "Keep your elbows fixed and squeeze at the top."),
        ]),
        saturday=_rest_day(),
        sunday=_rest_day(),
    ),
    "beginner__strength_training__equipment__3d__45min": _build_plan(
        "beginner__strength_training__equipment__3d__45min",
        difficulty="beginner",
        notes="A beginner strength training routine that prioritizes solid technique and consistent progression.",
        monday=_workout_day([
            _exercise("Squat", 3, 10, "Move with a full range of motion and keep your spine neutral."),
            _exercise("Dumbbell Fly", 3, 10, "Keep your shoulders down and back as you open and close."),
            _exercise("Bicep Curl", 3, 10, "Keep the movement slow and deliberate."),
        ]),
        tuesday=_rest_day(),
        wednesday=_workout_day([
            _exercise("Push-up", 3, 10, "Maintain a solid plank from head to heels."),
            _exercise("Squat", 3, 10, "Drive your hips up and keep your weight centered."),
            _exercise("Dumbbell Kickback", 3, 10, "Keep your wrists straight as you extend."),
        ]),
        thursday=_rest_day(),
        friday=_workout_day([
            _exercise("Squat", 3, 10, "Stand tall at the top and keep your chest open."),
            _exercise("Dumbbell Fly", 3, 10, "Focus on the mind-muscle connection."),
            _exercise("Bicep Curl", 3, 10, "Lower slowly and keep tension in the muscle."),
        ]),
        saturday=_rest_day(),
        sunday=_rest_day(),
    ),
    "beginner__general_fitness__no_equipment__3d__30min": _build_plan(
        "beginner__general_fitness__no_equipment__3d__30min",
        difficulty="beginner",
        notes="A general fitness routine that builds balanced strength and mobility using bodyweight movement.",
        monday=_workout_day([
            _exercise("Squat", 3, 12, "Keep your heels grounded and chest upright."),
            _exercise("Push-up", 3, 10, "Keep a steady tempo and full range of motion."),
        ]),
        tuesday=_rest_day(),
        wednesday=_workout_day([
            _exercise("Squat", 3, 12, "Keep your knees tracking straight."),
            _exercise("Push-up", 3, 10, "Control the descent with a tight core."),
        ]),
        thursday=_rest_day(),
        friday=_workout_day([
            _exercise("Squat", 3, 12, "Keep your back flat and gaze forward."),
            _exercise("Push-up", 3, 10, "Breathe steadily and keep your hips level."),
        ]),
        saturday=_rest_day(),
        sunday=_rest_day(),
    ),
    "beginner__flexibility__no_equipment__3d__30min": _build_plan(
        "beginner__flexibility__no_equipment__3d__30min",
        difficulty="beginner",
        notes="A low-impact beginner plan that emphasizes movement quality, flexibility, and gentle strength." ,
        monday=_workout_day([
            _exercise("Squat", 3, 12, "Use a slow tempo and focus on hip mobility."),
            _exercise("Push-up", 3, 10, "Keep your body aligned and move with control."),
        ]),
        tuesday=_rest_day(),
        wednesday=_workout_day([
            _exercise("Squat", 3, 10, "Sit into the movement and keep your back straight."),
            _exercise("Push-up", 3, 10, "Warm up the shoulders with steady repetitions."),
        ]),
        thursday=_rest_day(),
        friday=_workout_day([
            _exercise("Squat", 3, 12, "Focus on a smooth, controlled tempo."),
            _exercise("Push-up", 3, 10, "Keep your shoulders healthy by moving steadily."),
        ]),
        saturday=_rest_day(),
        sunday=_rest_day(),
    ),
    "beginner__endurance__no_equipment__3d__30min": _build_plan(
        "beginner__endurance__no_equipment__3d__30min",
        difficulty="beginner",
        notes="A beginner endurance plan that uses repeated bodyweight circuits and recovery days to improve stamina.",
        monday=_workout_day([
            _exercise("Squat", 3, 12, "Maintain a strong rhythm and consistent breathing."),
            _exercise("Push-up", 3, 12, "Keep each rep stable and steady."),
        ]),
        tuesday=_rest_day(),
        wednesday=_workout_day([
            _exercise("Squat", 3, 12, "Keep your core engaged for each repetition."),
            _exercise("Push-up", 3, 12, "Stay tall through your shoulders and hips."),
        ]),
        thursday=_rest_day(),
        friday=_workout_day([
            _exercise("Squat", 3, 12, "Keep a smooth tempo and move with endurance."),
            _exercise("Push-up", 3, 12, "Finish strong with consistent form."),
        ]),
        saturday=_rest_day(),
        sunday=_rest_day(),
    ),
    "intermediate__weight_loss__no_equipment__4d__45min": _build_plan(
        "intermediate__weight_loss__no_equipment__4d__45min",
        difficulty="intermediate",
        notes="An intermediate bodyweight weight-loss routine that balances higher volume with a mid-week recovery day.",
        monday=_workout_day([
            _exercise("Squat", 4, 12, "Keep your chest lifted and control the descent."),
            _exercise("Push-up", 4, 12, "Keep your elbows tucked and maintain tension."),
            _exercise("Squat", 3, 10, "Focus on strong body positioning."),
        ]),
        tuesday=_workout_day([
            _exercise("Push-up", 4, 12, "Keep your core braced and chest low."),
            _exercise("Squat", 3, 12, "Sit your hips back and push through your heels."),
            _exercise("Push-up", 3, 10, "Move with a steady tempo."),
        ]),
        wednesday=_rest_day(),
        thursday=_workout_day([
            _exercise("Squat", 4, 12, "Keep a full range of motion."),
            _exercise("Push-up", 4, 12, "Control the lowering phase."),
            _exercise("Squat", 3, 10, "Focus on breathing evenly."),
        ]),
        friday=_workout_day([
            _exercise("Push-up", 4, 12, "Stay strong through your shoulders."),
            _exercise("Squat", 4, 12, "Keep the core tight."),
            _exercise("Push-up", 3, 10, "Finish with good form."),
        ]),
        saturday=_rest_day(),
        sunday=_rest_day(),
    ),
    "intermediate__weight_loss__equipment__4d__45min": _build_plan(
        "intermediate__weight_loss__equipment__4d__45min",
        difficulty="intermediate",
        notes="A weight loss plan with equipment that maintains intensity and recovery across four training days.",
        monday=_workout_day([
            _exercise("Squat", 4, 12, "Move with control and keep your back flat."),
            _exercise("Push-up", 4, 12, "Keep your body aligned from head to heels."),
            _exercise("Dumbbell Fly", 3, 12, "Control the motion in your chest."),
        ]),
        tuesday=_workout_day([
            _exercise("Bicep Curl", 4, 12, "Keep your elbows fixed at your sides."),
            _exercise("Dumbbell Kickback", 4, 12, "Use a slow tempo and a full extension."),
            _exercise("Squat", 3, 10, "Keep your knees tracking over your toes."),
        ]),
        wednesday=_rest_day(),
        thursday=_workout_day([
            _exercise("Push-up", 4, 12, "Stay strong through the full range."),
            _exercise("Dumbbell Fly", 3, 12, "Squeeze the chest at the top."),
            _exercise("Squat", 3, 12, "Drive through the heels."),
        ]),
        friday=_workout_day([
            _exercise("Bicep Curl", 4, 12, "Lower with control."),
            _exercise("Dumbbell Kickback", 4, 12, "Keep your elbow elevated."),
            _exercise("Push-up", 3, 10, "Hold a tight plank."),
        ]),
        saturday=_rest_day(),
        sunday=_rest_day(),
    ),
    "intermediate__muscle_gain__equipment__4d__60min": _build_plan(
        "intermediate__muscle_gain__equipment__4d__60min",
        difficulty="intermediate",
        notes="A balanced intermediate muscle gain plan that uses equipment to stimulate hypertrophy across four days.",
        monday=_workout_day([
            _exercise("Squat", 4, 10, "Load your hips and keep your knees aligned."),
            _exercise("Dumbbell Fly", 4, 10, "Keep the chest engaged on each rep."),
            _exercise("Bicep Curl", 4, 10, "Contract at the top and lower slowly."),
        ]),
        tuesday=_workout_day([
            _exercise("Push-up", 4, 12, "Keep your spine neutral and core steady."),
            _exercise("Squat", 4, 10, "Keep your heels anchored."),
            _exercise("Dumbbell Kickback", 4, 12, "Focus on a strong triceps contraction."),
        ]),
        wednesday=_rest_day(),
        thursday=_workout_day([
            _exercise("Squat", 4, 10, "Keep the weight under control."),
            _exercise("Dumbbell Fly", 4, 10, "Maintain tension through the chest."),
            _exercise("Bicep Curl", 4, 10, "Use full range of motion."),
        ]),
        friday=_workout_day([
            _exercise("Push-up", 4, 12, "Keep your shoulders stable."),
            _exercise("Dumbbell Kickback", 4, 12, "Squeeze at the top of each rep."),
            _exercise("Squat", 4, 10, "Stay strong and controlled."),
        ]),
        saturday=_rest_day(),
        sunday=_rest_day(),
    ),
    "intermediate__strength_training__equipment__4d__60min": _build_plan(
        "intermediate__strength_training__equipment__4d__60min",
        difficulty="intermediate",
        notes="This intermediate strength plan uses equipment and four weekly sessions to build power and resilience.",
        monday=_workout_day([
            _exercise("Squat", 4, 10, "Keep your spine neutral and your core engaged."),
            _exercise("Dumbbell Fly", 4, 10, "Keep the elbows soft and the shoulders stable."),
            _exercise("Bicep Curl", 4, 10, "Control the weight on every rep."),
        ]),
        tuesday=_workout_day([
            _exercise("Push-up", 4, 12, "Maintain a straight line from head to heels."),
            _exercise("Dumbbell Kickback", 4, 12, "Keep your elbow high and stable."),
            _exercise("Squat", 4, 10, "Sit back into the movement."),
        ]),
        wednesday=_rest_day(),
        thursday=_workout_day([
            _exercise("Squat", 4, 10, "Use slow and controlled reps."),
            _exercise("Dumbbell Fly", 4, 10, "Keep a strong chest contraction."),
            _exercise("Bicep Curl", 4, 10, "Keep a controlled tempo."),
        ]),
        friday=_workout_day([
            _exercise("Push-up", 4, 12, "Use steady breathing."),
            _exercise("Dumbbell Kickback", 4, 12, "Focus on form over momentum."),
            _exercise("Squat", 4, 10, "Drive through the floor."),
        ]),
        saturday=_rest_day(),
        sunday=_rest_day(),
    ),
    "intermediate__general_fitness__no_equipment__4d__45min": _build_plan(
        "intermediate__general_fitness__no_equipment__4d__45min",
        difficulty="intermediate",
        notes="A general fitness plan for intermediate users that blends strength, endurance, and recovery." ,
        monday=_workout_day([
            _exercise("Squat", 4, 12, "Keep your core strong and posture tall."),
            _exercise("Push-up", 4, 12, "Move with control and consistency."),
            _exercise("Squat", 3, 10, "Keep your back flat."),
        ]),
        tuesday=_workout_day([
            _exercise("Push-up", 4, 12, "Maintain full range."),
            _exercise("Squat", 4, 12, "Drive through your heels."),
            _exercise("Push-up", 3, 10, "Stay tight through your midsection."),
        ]),
        wednesday=_rest_day(),
        thursday=_workout_day([
            _exercise("Squat", 4, 12, "Keep steady breathing."),
            _exercise("Push-up", 4, 12, "Stay aligned."),
            _exercise("Squat", 3, 10, "Use a controlled tempo."),
        ]),
        friday=_workout_day([
            _exercise("Push-up", 4, 12, "Hold a strong plank."),
            _exercise("Squat", 4, 12, "Keep knees tracking straight."),
            _exercise("Push-up", 3, 10, "Finish strong."),
        ]),
        saturday=_rest_day(),
        sunday=_rest_day(),
    ),
    "intermediate__flexibility__no_equipment__4d__30min": _build_plan(
        "intermediate__flexibility__no_equipment__4d__30min",
        difficulty="intermediate",
        notes="A flexibility-focused routine that supports movement quality while preserving strength." ,
        monday=_workout_day([
            _exercise("Squat", 3, 10, "Move through a full range of motion."),
            _exercise("Push-up", 3, 10, "Keep your shoulders active."),
            _exercise("Squat", 3, 10, "Focus on stability."),
        ]),
        tuesday=_workout_day([
            _exercise("Push-up", 3, 10, "Keep your spine long."),
            _exercise("Squat", 3, 10, "Maintain good form."),
            _exercise("Push-up", 3, 10, "Breathe steadily."),
        ]),
        wednesday=_rest_day(),
        thursday=_workout_day([
            _exercise("Squat", 3, 10, "Keep your hips mobile."),
            _exercise("Push-up", 3, 10, "Move slowly and carefully."),
            _exercise("Squat", 3, 10, "Keep your knees comfortable."),
        ]),
        friday=_workout_day([
            _exercise("Push-up", 3, 10, "Focus on control."),
            _exercise("Squat", 3, 10, "Use a steady tempo."),
            _exercise("Push-up", 3, 10, "Keep the movement smooth."),
        ]),
        saturday=_rest_day(),
        sunday=_rest_day(),
    ),
    "intermediate__endurance__no_equipment__4d__45min": _build_plan(
        "intermediate__endurance__no_equipment__4d__45min",
        difficulty="intermediate",
        notes="An endurance plan for intermediate users that builds stamina with four focused bodyweight workouts.",
        monday=_workout_day([
            _exercise("Squat", 4, 15, "Keep your pace even and controlled."),
            _exercise("Push-up", 4, 15, "Stay strong through each rep."),
            _exercise("Squat", 3, 12, "Maintain good form."),
        ]),
        tuesday=_workout_day([
            _exercise("Push-up", 4, 15, "Breathe consistently."),
            _exercise("Squat", 4, 15, "Stay light on your feet."),
            _exercise("Push-up", 3, 12, "Keep your body aligned."),
        ]),
        wednesday=_rest_day(),
        thursday=_workout_day([
            _exercise("Squat", 4, 15, "Keep moving with stamina."),
            _exercise("Push-up", 4, 15, "Use a steady tempo."),
            _exercise("Squat", 3, 12, "Stay consistent."),
        ]),
        friday=_workout_day([
            _exercise("Push-up", 4, 15, "Keep your shoulders stable."),
            _exercise("Squat", 4, 15, "Keep the motion smooth."),
            _exercise("Push-up", 3, 12, "Finish with good control."),
        ]),
        saturday=_rest_day(),
        sunday=_rest_day(),
    ),
    "advanced__weight_loss__equipment__5d__60min": _build_plan(
        "advanced__weight_loss__equipment__5d__60min",
        difficulty="advanced",
        notes="A high-volume advanced weight loss plan that mixes strength and conditioning with two weekend recovery days.",
        monday=_workout_day([
            _exercise("Squat", 4, 15, "Push through your heels and keep your spine neutral."),
            _exercise("Push-up", 4, 15, "Keep your body in a straight line."),
            _exercise("Dumbbell Fly", 4, 12, "Focus on a strong chest contraction."),
            _exercise("Bicep Curl", 4, 12, "Use controlled motion and keep elbows stable."),
        ]),
        tuesday=_workout_day([
            _exercise("Squat", 4, 15, "Keep a steady tempo."),
            _exercise("Dumbbell Kickback", 4, 15, "Extend fully and squeeze the triceps."),
            _exercise("Push-up", 4, 15, "Control the lowering phase."),
            _exercise("Bicep Curl", 4, 12, "Keep the movement smooth."),
        ]),
        wednesday=_workout_day([
            _exercise("Squat", 4, 15, "Stay tall and stable."),
            _exercise("Dumbbell Fly", 4, 12, "Move with control."),
            _exercise("Push-up", 4, 15, "Keep your core braced."),
            _exercise("Dumbbell Kickback", 4, 15, "Keep elbows steady."),
        ]),
        thursday=_workout_day([
            _exercise("Squat", 4, 15, "Keep your weight balanced."),
            _exercise("Push-up", 4, 15, "Focus on steady form."),
            _exercise("Bicep Curl", 4, 12, "Squeeze at the top."),
            _exercise("Dumbbell Fly", 4, 12, "Maintain a strong chest connection."),
        ]),
        friday=_workout_day([
            _exercise("Squat", 4, 15, "Keep a strong hip drive."),
            _exercise("Push-up", 4, 15, "Keep your body aligned."),
            _exercise("Bicep Curl", 4, 12, "Lower with control."),
            _exercise("Dumbbell Kickback", 4, 15, "Keep the motion deliberate."),
        ]),
        saturday=_rest_day(),
        sunday=_rest_day(),
    ),
    "advanced__muscle_gain__equipment__5d__60min": _build_plan(
        "advanced__muscle_gain__equipment__5d__60min",
        difficulty="advanced",
        notes="A high-volume muscle gain schedule that targets all major muscle groups with equipment over five training days.",
        monday=_workout_day([
            _exercise("Squat", 4, 12, "Stay strong through the whole rep."),
            _exercise("Dumbbell Fly", 4, 12, "Squeeze at the top."),
            _exercise("Bicep Curl", 4, 12, "Keep elbows steady."),
            _exercise("Dumbbell Kickback", 4, 12, "Fully extend your triceps."),
        ]),
        tuesday=_workout_day([
            _exercise("Squat", 4, 12, "Use a controlled tempo."),
            _exercise("Push-up", 4, 15, "Maintain a full plank."),
            _exercise("Dumbbell Fly", 4, 12, "Control the motion."),
            _exercise("Bicep Curl", 4, 12, "Pause briefly at the top."),
        ]),
        wednesday=_workout_day([
            _exercise("Squat", 4, 12, "Keep your chest up."),
            _exercise("Push-up", 4, 15, "Keep shoulders stable."),
            _exercise("Dumbbell Kickback", 4, 12, "Keep elbows high."),
            _exercise("Dumbbell Fly", 4, 12, "Keep tension in your chest."),
        ]),
        thursday=_workout_day([
            _exercise("Squat", 4, 12, "Drive through your heels."),
            _exercise("Push-up", 4, 15, "Stay tight through the core."),
            _exercise("Bicep Curl", 4, 12, "Lower slowly."),
            _exercise("Dumbbell Kickback", 4, 12, "Keep momentum under control."),
        ]),
        friday=_workout_day([
            _exercise("Squat", 4, 12, "Keep your knees tracking."),
            _exercise("Push-up", 4, 15, "Breathe evenly."),
            _exercise("Dumbbell Fly", 4, 12, "Keep chest high."),
            _exercise("Bicep Curl", 4, 12, "Control the weights."),
        ]),
        saturday=_rest_day(),
        sunday=_rest_day(),
    ),
    "advanced__strength_training__equipment__5d__60min": _build_plan(
        "advanced__strength_training__equipment__5d__60min",
        difficulty="advanced",
        notes="An advanced strength training plan focused on consistency, heavy sets, and five days of lifting." ,
        monday=_workout_day([
            _exercise("Squat", 4, 12, "Keep your core braced and chest lifted."),
            _exercise("Dumbbell Fly", 4, 12, "Maintain tight shoulders."),
            _exercise("Bicep Curl", 4, 12, "Keep the elbows in place."),
            _exercise("Dumbbell Kickback", 4, 12, "Fully extend the arm."),
        ]),
        tuesday=_workout_day([
            _exercise("Squat", 4, 12, "Control the descent."),
            _exercise("Push-up", 4, 15, "Stay rigid through the torso."),
            _exercise("Dumbbell Fly", 4, 12, "Focus on the chest contraction."),
            _exercise("Bicep Curl", 4, 12, "Move deliberately."),
        ]),
        wednesday=_workout_day([
            _exercise("Squat", 4, 12, "Keep the movement balanced."),
            _exercise("Push-up", 4, 15, "Keep the body aligned."),
            _exercise("Dumbbell Kickback", 4, 12, "Squeeze your triceps."),
            _exercise("Dumbbell Fly", 4, 12, "Keep tension throughout."),
        ]),
        thursday=_workout_day([
            _exercise("Squat", 4, 12, "Stay strong through the whole set."),
            _exercise("Push-up", 4, 15, "Use full range of motion."),
            _exercise("Bicep Curl", 4, 12, "Keep your wrists straight."),
            _exercise("Dumbbell Kickback", 4, 12, "Keep the motion controlled."),
        ]),
        friday=_workout_day([
            _exercise("Squat", 4, 12, "Drive through your heels."),
            _exercise("Push-up", 4, 15, "Keep elbows tucked."),
            _exercise("Dumbbell Fly", 4, 12, "Maintain a strong chest connection."),
            _exercise("Bicep Curl", 4, 12, "Lower slowly."),
        ]),
        saturday=_rest_day(),
        sunday=_rest_day(),
    ),
    "advanced__endurance__no_equipment__5d__60min": _build_plan(
        "advanced__endurance__no_equipment__5d__60min",
        difficulty="advanced",
        notes="An advanced endurance plan with five bodyweight sessions designed to improve stamina and movement efficiency.",
        monday=_workout_day([
            _exercise("Squat", 4, 20, "Keep a strong, steady rhythm."),
            _exercise("Push-up", 4, 15, "Breathe consistently and stay aligned."),
            _exercise("Squat", 4, 15, "Stay smooth through each rep."),
            _exercise("Push-up", 3, 12, "Finish strong with form."),
        ]),
        tuesday=_workout_day([
            _exercise("Squat", 4, 20, "Maintain good posture."),
            _exercise("Push-up", 4, 15, "Keep your core engaged."),
            _exercise("Squat", 4, 15, "Control the descent."),
            _exercise("Push-up", 3, 12, "Stay steady."),
        ]),
        wednesday=_rest_day(),
        thursday=_workout_day([
            _exercise("Squat", 4, 20, "Keep moving with endurance."),
            _exercise("Push-up", 4, 15, "Keep your shoulders stable."),
            _exercise("Squat", 4, 15, "Breathe evenly."),
            _exercise("Push-up", 3, 12, "Keep your body aligned."),
        ]),
        friday=_workout_day([
            _exercise("Squat", 4, 20, "Stay steady and controlled."),
            _exercise("Push-up", 4, 15, "Hold your form."),
            _exercise("Squat", 4, 15, "Keep your knees aligned."),
            _exercise("Push-up", 3, 12, "Finish with control."),
        ]),
        saturday=_rest_day(),
        sunday=_rest_day(),
    ),
    "advanced__general_fitness__equipment__5d__60min": _build_plan(
        "advanced__general_fitness__equipment__5d__60min",
        difficulty="advanced",
        notes="A varied advanced fitness plan using equipment for a balanced five-day routine.",
        monday=_workout_day([
            _exercise("Squat", 4, 12, "Keep your torso upright."),
            _exercise("Dumbbell Fly", 4, 12, "Focus on a strong chest contraction."),
            _exercise("Bicep Curl", 4, 12, "Control the descent."),
            _exercise("Push-up", 4, 15, "Keep a stable plank."),
        ]),
        tuesday=_workout_day([
            _exercise("Squat", 4, 12, "Drive through your heels."),
            _exercise("Dumbbell Kickback", 4, 12, "Keep the elbow elevated."),
            _exercise("Push-up", 4, 15, "Stay aligned."),
            _exercise("Bicep Curl", 4, 12, "Keep tension in your arms."),
        ]),
        wednesday=_rest_day(),
        thursday=_workout_day([
            _exercise("Squat", 4, 12, "Keep your hips stable."),
            _exercise("Dumbbell Fly", 4, 12, "Squeeze at the top."),
            _exercise("Bicep Curl", 4, 12, "Use a smooth pace."),
            _exercise("Push-up", 4, 15, "Maintain full range."),
        ]),
        friday=_workout_day([
            _exercise("Squat", 4, 12, "Stay strong through the rep."),
            _exercise("Dumbbell Kickback", 4, 12, "Hold the top position."),
            _exercise("Push-up", 4, 15, "Keep your shoulders back."),
            _exercise("Bicep Curl", 4, 12, "Focus on control."),
        ]),
        saturday=_rest_day(),
        sunday=_rest_day(),
    ),
    "advanced__flexibility__no_equipment__4d__45min": _build_plan(
        "advanced__flexibility__no_equipment__4d__45min",
        difficulty="advanced",
        notes="An advanced flexibility routine that maintains four consistent sessions for mobility and active recovery.",
        monday=_workout_day([
            _exercise("Squat", 4, 12, "Focus on depth and controlled motion."),
            _exercise("Push-up", 4, 12, "Keep your shoulders mobile."),
            _exercise("Squat", 3, 10, "Keep your breath steady."),
        ]),
        tuesday=_workout_day([
            _exercise("Push-up", 4, 12, "Keep your core engaged."),
            _exercise("Squat", 4, 12, "Use a controlled cadence."),
            _exercise("Push-up", 3, 10, "Stay aligned."),
        ]),
        wednesday=_rest_day(),
        thursday=_workout_day([
            _exercise("Squat", 4, 12, "Keep the movement smooth."),
            _exercise("Push-up", 4, 12, "Focus on full range."),
            _exercise("Squat", 3, 10, "Keep your knees comfortable."),
        ]),
        friday=_workout_day([
            _exercise("Push-up", 4, 12, "Move with steady control."),
            _exercise("Squat", 4, 12, "Maintain good posture."),
            _exercise("Push-up", 3, 10, "Keep tension through your body."),
        ]),
        saturday=_rest_day(),
        sunday=_rest_day(),
    ),
    "advanced__sports_specific__equipment__5d__60min": _build_plan(
        "advanced__sports_specific__equipment__5d__60min",
        difficulty="advanced",
        notes="A sports-specific schedule that uses five days of targeted equipment training for power and coordination.",
        monday=_workout_day([
            _exercise("Squat", 4, 12, "Drive through the heels and stay balanced."),
            _exercise("Dumbbell Fly", 4, 12, "Keep the shoulder blades engaged."),
            _exercise("Bicep Curl", 4, 12, "Use a smooth tempo."),
            _exercise("Dumbbell Kickback", 4, 12, "Keep your elbow steady."),
        ]),
        tuesday=_workout_day([
            _exercise("Squat", 4, 12, "Stay centered and strong."),
            _exercise("Push-up", 4, 15, "Keep your core tight."),
            _exercise("Dumbbell Fly", 4, 12, "Control the movement."),
            _exercise("Bicep Curl", 4, 12, "Keep your wrist neutral."),
        ]),
        wednesday=_workout_day([
            _exercise("Squat", 4, 12, "Keep the motion steady."),
            _exercise("Push-up", 4, 15, "Stay long through the spine."),
            _exercise("Dumbbell Kickback", 4, 12, "Push through the triceps."),
            _exercise("Dumbbell Fly", 4, 12, "Maintain tension in your chest."),
        ]),
        thursday=_workout_day([
            _exercise("Squat", 4, 12, "Keep your hips stable."),
            _exercise("Push-up", 4, 15, "Keep the shoulders aligned."),
            _exercise("Bicep Curl", 4, 12, "Lower the weight slowly."),
            _exercise("Dumbbell Kickback", 4, 12, "Fully extend your arm."),
        ]),
        friday=_workout_day([
            _exercise("Squat", 4, 12, "Keep a smooth cadence."),
            _exercise("Push-up", 4, 15, "Keep your body steady."),
            _exercise("Dumbbell Fly", 4, 12, "Squeeze at the top."),
            _exercise("Bicep Curl", 4, 12, "Keep the path clean."),
        ]),
        saturday=_rest_day(),
        sunday=_rest_day(),
    ),
}
