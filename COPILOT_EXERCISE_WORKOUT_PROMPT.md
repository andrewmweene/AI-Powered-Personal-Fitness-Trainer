# Copilot Prompt — Exercise Workflow Redesign

> **How to use:**
> 1. Open GitHub Copilot Chat in VS Code (`Ctrl+Shift+I`)
> 2. Paste the entire prompt block below and send it
> 3. Copilot will modify Exercise.jsx and create ExerciseInstructions.jsx
> 4. Review each generated file against the checklist at the bottom

---

## Prompt — paste into Copilot Chat

```
I need to redesign the Exercise page of my AI Personal Trainer React app.
The backend (FastAPI), database (Supabase/PostgreSQL), and pose engine
(MediaPipe) are unchanged. Only the frontend React components change.

## Overview of changes

The exercise page must now support two modes:
  1. Single exercise mode — user picks one exercise and does as many reps
     as they want
  2. Full workout session mode — system loads the user's recommended plan
     for today, guides them through each exercise in order with the exact
     sets and reps from their plan, then auto-advances to the next exercise

The exercise screen layout must be redesigned:
  - Camera feed takes the top section (60% of viewport height)
  - Feedback panel sits DIRECTLY below the camera feed (not in a side column)
  - Two tab buttons sit below the feedback panel:
      "Start exercise" — shows the live camera/rep counter view
      "How to do it"  — shows step-by-step instructions for the current exercise
  - Stats panel (reps, accuracy, state) moves to below the tab content area

---

## Files to CREATE

### `frontend/src/pages/ExerciseInstructions.jsx`

This is NOT a separate page — it is a component rendered inside the
Exercise page when the user clicks the "How to do it" tab.

Props: exercise (string — the current exercise name)

Implement static instruction content for all 5 exercises.
Each exercise has:
  - A short description (1-2 sentences)
  - "Starting position" — bullet list of 3-4 points
  - "Movement" — numbered list of 4-5 steps
  - "Common mistakes" — bullet list of 3 mistakes to avoid
  - "Muscles worked" — comma-separated list

Content for each exercise:

SQUAT:
  description: "A fundamental lower-body exercise that targets the
    quadriceps, hamstrings, and glutes. Essential for building leg
    strength and improving mobility."
  starting position:
    - Stand with feet shoulder-width apart, toes pointing slightly outward
    - Keep your chest up and spine neutral
    - Arms extended forward for balance or crossed at chest
    - Weight evenly distributed through both feet
  movement:
    1. Brace your core and take a deep breath
    2. Push your hips back and bend your knees simultaneously
    3. Lower until thighs are parallel to the floor (or as deep as comfortable)
    4. Drive through your heels to return to standing
    5. Exhale at the top and squeeze glutes
  common mistakes:
    - Knees caving inward — push them out in line with toes
    - Heels rising off the floor — improve ankle mobility or elevate heels slightly
    - Rounding the lower back — engage core throughout and keep chest up
  muscles worked: Quadriceps, Hamstrings, Glutes, Core, Calves

BICEP CURL:
  description: "An isolation exercise targeting the biceps brachii.
    Builds arm strength and size when performed with controlled movement."
  starting position:
    - Stand with feet hip-width apart
    - Hold dumbbells at your sides with palms facing forward
    - Keep elbows pinned close to your torso
    - Shoulders relaxed and down
  movement:
    1. Keeping upper arms stationary, exhale and curl weights toward shoulders
    2. Supinate (rotate) your wrists at the top so pinkies point toward ceiling
    3. Squeeze biceps hard at peak contraction
    4. Slowly lower weights back to starting position (3 seconds down)
    5. Fully extend arms at the bottom — do not lock elbows
  common mistakes:
    - Swinging the torso to lift the weight — reduce weight and control the movement
    - Not fully extending at the bottom — limits range of motion and growth
    - Elbows drifting forward — keep them pinned to your sides throughout
  muscles worked: Biceps brachii, Brachialis, Forearms

PUSH-UP:
  description: "A classic bodyweight exercise that builds upper body
    and core strength. Highly versatile and requires no equipment."
  starting position:
    - Place hands slightly wider than shoulder-width
    - Arms fully extended, body forms a straight line from head to heels
    - Feet together or hip-width apart
    - Core tight, glutes engaged, neck neutral
  movement:
    1. Take a breath and brace your core
    2. Lower your chest to the floor by bending elbows at 45 degrees to your body
    3. Keep elbows from flaring out wide
    4. Lower until chest is 2-3cm from the floor
    5. Press through palms to return to start — exhale on the way up
  common mistakes:
    - Hips sagging — engage core throughout the entire movement
    - Elbows flaring out at 90 degrees — keep them at 45 degrees
    - Partial range of motion — chest should nearly touch the floor each rep
  muscles worked: Pectorals, Triceps, Anterior deltoids, Core

DUMBBELL FLY:
  description: "A chest isolation exercise that stretches and contracts
    the pectoral muscles through a wide arc of motion."
  starting position:
    - Lie flat on a bench or floor with a dumbbell in each hand
    - Arms extended directly above chest, palms facing each other
    - Maintain a slight bend in the elbows throughout
    - Shoulder blades retracted and pressed into the bench
  movement:
    1. Take a breath and lower arms in a wide arc to your sides
    2. Keep the slight elbow bend — do not let them straighten
    3. Lower until you feel a good stretch in your chest (upper arms parallel to floor)
    4. Squeeze chest muscles to bring arms back up through the same arc
    5. Dumbbells should not touch at the top — stop when hands are above shoulders
  common mistakes:
    - Straightening arms completely — turns it into a press and strains elbows
    - Going too heavy — reduces control and increases injury risk
    - Not feeling the stretch at the bottom — focus on the chest contraction, not the weight
  muscles worked: Pectoralis major, Anterior deltoids, Biceps (stabiliser)

DUMBBELL KICKBACK:
  description: "A tricep isolation exercise performed bent over. Highly
    effective for building the back of the upper arm."
  starting position:
    - Hinge forward at the hips until torso is nearly parallel to the floor
    - Hold a dumbbell in each hand with upper arms parallel to the floor
    - Elbows bent at 90 degrees, hugged close to your sides
    - Core engaged, spine neutral
  movement:
    1. Keeping upper arm completely still, exhale and extend the forearm back
    2. Straighten arm until fully extended — pause for 1 second
    3. Squeeze tricep hard at full extension
    4. Slowly lower the forearm back to 90 degrees (2-3 seconds)
    5. Do not swing or use momentum
  common mistakes:
    - Upper arm dropping — it must stay parallel to the floor throughout
    - Using momentum to swing the weight — slow and controlled
    - Not reaching full extension — the lockout is where the tricep contracts most
  muscles worked: Triceps brachii (all three heads), Posterior deltoids

Render this component as a clean card layout:
  - Exercise name as the heading
  - Description in muted text below
  - Four sections rendered as collapsible cards or plain sections:
    Starting position, Movement, Common mistakes, Muscles worked
  - Use lucide-react icons: Target for starting position, Play for movement,
    AlertCircle for mistakes, Dumbbell for muscles worked
  - Styling: white card with border, padding, rounded corners using Tailwind
  - No camera, no API calls — purely static content

---

### `frontend/src/components/exercise/ModeSelector.jsx`

A modal/prompt shown when the user first opens the Exercise page.
The user must choose a mode before seeing the camera.

Props:
  onSelectSingle: () => void
  onSelectFullWorkout: () => void
  todaysPlan: object | null  (the day's exercises from the workout plan)
  isLoading: boolean          (true while fetching the plan)

Render as a centred card (not a browser modal — a React div styled as a modal):
  Heading: "How would you like to train today?"
  Subheading: "Choose your workout mode"

  Two option cards side by side (or stacked on mobile):

  Card 1 — "Single exercise"
    Icon: Dumbbell (lucide)
    Description: "Pick one exercise and do it at your own pace"
    Button: "Choose exercise →" — calls onSelectSingle()

  Card 2 — "Full workout session"
    Icon: CalendarDays (lucide)
    Description: "Follow today's plan from start to finish"
    If isLoading: show a small spinner inside the card
    If todaysPlan is null or has no exercises today (is_rest: true):
      Show muted text: "Today is a rest day in your plan"
      Disable the button, show it greyed out
    If todaysPlan has exercises:
      Show a small preview list of exercise names under the description
      e.g. "Squat · Bicep Curl · Push-up"
    Button: "Start full workout →" — calls onSelectFullWorkout()
      Disabled if today is a rest day

  Below both cards: text link "Set up my plan →" navigates to /plan

---

### `frontend/src/components/exercise/WorkoutProgress.jsx`

Shown only during full workout session mode. Displays progress through
the plan's exercises for the current day.

Props:
  exercises: array of {exercise, sets, reps, notes}
  currentIndex: number  (0-based index of the active exercise)
  completedSets: number  (sets completed for the current exercise)

Render as a horizontal step indicator bar:
  - Each exercise shown as a pill/chip
  - Completed exercises: green background, checkmark icon
  - Current exercise: blue background, pulsing dot or bold text
  - Upcoming exercises: grey background, muted text
  - Below the pills: "Exercise {currentIndex+1} of {exercises.length}"
    and "Set {completedSets+1} of {exercises[currentIndex].sets}"
    and "{exercises[currentIndex].reps} reps target"
  - When all sets for an exercise are done: show a "Next exercise →" button

---

### `frontend/src/components/exercise/FeedbackPanel.jsx`

Extracted component for the feedback display area that sits directly
below the camera feed.

Props:
  feedback: string       (corrective text from pose API)
  state: string          (REST / TRANSITION / COMPLETE)
  repCount: number
  targetReps: number | null  (null in single mode — no target)
  accuracy: number       (0-100)

Render as a full-width panel with light background:

  Row 1 — three metric chips in a row:
    Reps: "{repCount}{targetReps ? ' / ' + targetReps : ''}"
      If repCount >= targetReps and targetReps is not null: show in green
    State: current state text
      REST → grey pill · TRANSITION → amber pill · COMPLETE → green pill
    Accuracy: "{accuracy}%"
      >= 80: green text · 60-79: amber · < 60: red

  Row 2 — feedback text box (full width):
    Light yellow background if feedback is non-empty
    Light grey background if feedback is empty
    Show feedback text in dark text, or "Looking good! Keep it up." if empty
    Text is 14px, centred, italic

  Row 3 — rep progress bar (only shown when targetReps is not null):
    A horizontal progress bar showing repCount / targetReps
    Fills green as reps increase
    Shows "Target reached!" text and turns fully green when repCount >= targetReps

---

## Files to MODIFY

### `frontend/src/pages/Exercise.jsx`

Completely redesign this page. Keep all existing hook imports and API
logic — only change the layout, state management for mode, and how
components are assembled.

#### New state variables to add

```js
// Mode selection
const [mode, setMode] = useState(null)
// null = not chosen yet, 'single' = single exercise, 'workout' = full session

// Full workout session state
const [todaysPlan, setTodaysPlan] = useState(null)
const [planLoading, setPlanLoading] = useState(false)
const [currentExerciseIndex, setCurrentExerciseIndex] = useState(0)
const [completedSets, setCompletedSets] = useState(0)
const [sessionSummaries, setSessionSummaries] = useState([])
// Array of completed exercise summaries for the final done screen

// Tab state for the two buttons below the camera
const [activeTab, setActiveTab] = useState('exercise')
// 'exercise' = camera/rep view | 'instructions' = how-to view

// Target reps (comes from plan in workout mode, null in single mode)
const [targetReps, setTargetReps] = useState(null)
```

#### On component mount (useEffect)

Fetch the current week's workout plan:
  GET /recommendations/plan
  Extract today's day (use new Date().toLocaleDateString('en-US',{weekday:'long'}).toLowerCase())
  Store the day's exercises array in todaysPlan
  If the day is a rest day or has no exercises, set todaysPlan to null

#### Mode selection flow

If mode is null:
  Render only the ModeSelector component (centred on the page, no camera)
  Do not activate the webcam yet

If mode === 'single':
  Show an exercise selector dropdown (the existing one)
  Set targetReps = null
  Proceed to the camera screen

If mode === 'workout':
  Load exercises from todaysPlan
  Set the current exercise to exercises[currentExerciseIndex]
  Set targetReps = exercises[currentExerciseIndex].reps
  Remove the exercise selector (exercise is locked to the plan)
  Show WorkoutProgress component above the camera

#### New layout structure (when mode is selected)

Replace the existing two-column grid with this single-column layout:

```
┌─────────────────────────────────────────┐
│  [WorkoutProgress] (only in workout     │
│   mode — full width horizontal bar)     │
├─────────────────────────────────────────┤
│                                         │
│         CAMERA FEED                     │
│    <video> element, width: 100%         │
│    aspect-ratio: 4/3 or 16/9           │
│                                         │
├─────────────────────────────────────────┤
│  FEEDBACK PANEL (FeedbackPanel.jsx)     │
│  Full width, directly below camera      │
├─────────────────────────────────────────┤
│  [  ▶ Start exercise  ] [  ? How to do it  ]  │
│  Two tab buttons, full width, side by side    │
├─────────────────────────────────────────┤
│  TAB CONTENT AREA                       │
│  'exercise' tab: Start/Stop buttons,    │
│    session summary after stopping       │
│  'instructions' tab: ExerciseInstructions│
│    component for the current exercise   │
└─────────────────────────────────────────┘
```

#### Tab button styling

Two full-width buttons side by side using Tailwind grid-cols-2:

Start exercise tab button (active state):
  background: primary blue (bg-primary / #1976D2)
  text: white
  icon: Play (lucide, 16px)
  label: "Start exercise"

How to do it tab button (active state):
  background: primary blue
  text: white
  icon: HelpCircle (lucide, 16px)
  label: "How to do it"

Inactive tab button:
  background: white with border
  text: gray

#### Full workout auto-advance logic

When repCount >= targetReps AND isRunning is true:
  1. Automatically stop the session (set isRunning to false)
  2. Wait 2 seconds (setTimeout)
  3. Save the session via POST /sessions/
  4. Push session summary to sessionSummaries array
  5. If currentExerciseIndex + 1 < todaysPlan.exercises.length:
       Increment currentExerciseIndex
       Reset repCount, correctReps, incorrectReps via reset()
       Set targetReps to next exercise's reps
       Increment completedSets if same exercise, or reset to 0 if new exercise
       Set isRunning to true automatically to start the next exercise
  6. If all exercises complete:
       Navigate to a done screen (render inline — not a separate page):
         "Workout complete! 🎉"
         Summary table of all exercises done
         Total reps, avg accuracy
         "View dashboard" button → navigate('/dashboard')

#### Single mode behaviour (unchanged from current)

When mode === 'single':
  User selects exercise from dropdown
  No target reps
  Manual Start/Stop
  On Stop: show summary, save session, offer to restart or go to dashboard

#### Sets handling in workout mode

Each exercise in the plan has a "sets" value (e.g. 3 sets × 10 reps).
Handle sets as follows:
  - completedSets tracks how many sets are done for the current exercise
  - When targetReps is reached: show "Set {n} complete" message
  - Show a "Rest 60 seconds" countdown (a simple useEffect countdown from 60 to 0)
  - After rest (or user skips rest): automatically start the next set
  - After all sets for the exercise are done: advance to the next exercise in the plan

Rest countdown component (implement inline in Exercise.jsx):
  A simple countdown timer showing "Rest: {seconds}s"
  Displayed in the feedback panel area during rest
  A "Skip rest" button advances immediately

---

## Coding standards

- All new components: functional, with JSDoc prop documentation
- All props: destructured with defaults where appropriate
- No inline styles: Tailwind classes only
- FeedbackPanel, WorkoutProgress, ModeSelector: pure display components
  (no API calls, no hooks — props only)
- All API calls remain in Exercise.jsx as they currently are
- The webcam (useWebcam hook) is NOT activated until mode is selected
  (prevents the browser from requesting camera permission on the mode
  selection screen)
- The usePoseSession hook is NOT started until isRunning is true
- All timeouts (auto-advance, rest countdown) must be cleared in
  useEffect cleanup functions to prevent memory leaks
- On mobile (< 768px): tab buttons stack vertically, camera is full width
- Accessibility: tab buttons must have aria-selected and role="tab"
```

---

## POST-GENERATION CHECKLIST

Work through each item after Copilot generates the files:

### ModeSelector
- [ ] Renders centred on screen without showing camera
- [ ] Full workout card shows today's exercise names as a preview
- [ ] Rest day disables the Full workout button
- [ ] "Set up my plan" link navigates to /plan

### Exercise screen layout
- [ ] Camera feed is full width (no side-by-side layout)
- [ ] FeedbackPanel is directly below the camera with no gap
- [ ] Two tab buttons are directly below FeedbackPanel
- [ ] Clicking "How to do it" shows instructions without camera disappearing

### FeedbackPanel
- [ ] Rep counter shows "X / Y" format in workout mode, "X" in single mode
- [ ] Progress bar fills as reps increase toward target
- [ ] State pill changes colour (grey/amber/green) correctly
- [ ] "Target reached!" text appears and bar turns fully green at target

### WorkoutProgress (workout mode only)
- [ ] Shows all exercises for today as pills
- [ ] Current exercise highlighted in blue
- [ ] Completed exercises show green with checkmark
- [ ] Set counter and rep target shown correctly

### Auto-advance (workout mode only)
- [ ] Session auto-saves when targetReps is reached
- [ ] Rest countdown appears after target is reached
- [ ] "Skip rest" button works
- [ ] Next exercise loads automatically after rest
- [ ] Done screen appears after all exercises completed
- [ ] Done screen shows total reps and average accuracy

### Instructions tab
- [ ] All 5 exercises have content
- [ ] Switching tab does not interrupt a running session
- [ ] Switching back to "Start exercise" tab shows current rep count
```
