# Copilot Prompt — Migrate Frontend from Streamlit to React

> **How to use:**
> 1. Open GitHub Copilot Chat in VS Code (`Ctrl+Shift+I`)
> 2. Paste the entire prompt block below and send it
> 3. Copilot will scaffold the full React frontend structure
> 4. Open `REACT_MIGRATION_GUIDE.md` for step-by-step implementation instructions

---

## Prompt — paste into Copilot Chat

```
I am migrating the frontend of my AI Personal Trainer project from Streamlit
to React. The FastAPI backend, PostgreSQL database, MediaPipe pose engine, and
all business logic remain completely unchanged. Only the frontend/ folder is
being replaced.

## Current backend (already built — do not modify these)

FastAPI running on http://localhost:8000 with these existing endpoints:

AUTH:
  POST   /users/register         → { id, username, email, ... }
  POST   /users/login            → { access_token, token_type }
  GET    /users/me               → current user profile

ONBOARDING:
  POST   /onboarding/complete    → { profile, plan }
  GET    /onboarding/status      → { onboarding_complete: bool }
  GET    /onboarding/profile     → full user profile

SESSIONS:
  POST   /sessions/              → save exercise session
  GET    /sessions/              → list user sessions

ANALYTICS:
  GET    /analytics/summary      → { total_sessions, total_reps, avg_accuracy,
                                     current_streak_days, best_streak_days,
                                     sessions_this_week }
  GET    /analytics/weekly       → [ { date, session_count, avg_accuracy } ]
  GET    /analytics/by-exercise  → [ { exercise, count, avg_accuracy } ]
  GET    /analytics/accuracy-trend → [ { session_num, accuracy } ]

RECOMMENDATIONS:
  GET    /recommendations/plan   → current week workout plan
  POST   /recommendations/plan/refresh → regenerate plan

POSE (new endpoint — generate this too):
  POST   /pose/analyse-frame     → accepts multipart/form-data with:
                                    file: JPEG image (video frame)
                                    exercise: string (exercise name)
                                    session_id: string (UUID)
                                   returns JSON:
                                    { angle: float, state: string,
                                      rep_completed: bool, correct: bool,
                                      feedback: string, rep_count: int,
                                      correct_reps: int, incorrect_reps: int }

All protected endpoints require header: Authorization: Bearer <token>
Tokens are JWT strings stored in localStorage under the key "token".

---

## Tech stack for the React frontend

- React 18 with Vite (not Create React App)
- React Router DOM v6 (file-based page routing)
- Axios (HTTP client — replaces Python requests)
- Tailwind CSS (utility styling — no custom CSS files)
- Recharts (charts — replaces Plotly)
- Lucide React (icons)
- React Hook Form (form handling for onboarding wizard)

---

## Project structure to generate

Replace the existing frontend/ folder entirely with:

frontend/
├── index.html
├── vite.config.js
├── tailwind.config.js
├── postcss.config.js
├── package.json
├── .env.example              (VITE_API_BASE_URL=http://localhost:8000)
└── src/
    ├── main.jsx              (React entry point)
    ├── App.jsx               (Router setup, AuthProvider wrapper)
    ├── index.css             (Tailwind directives only)
    │
    ├── api/
    │   ├── client.js         (Axios instance with JWT interceptor)
    │   ├── auth.js           (login, register, getMe API functions)
    │   ├── onboarding.js     (completeOnboarding, getStatus, getProfile)
    │   ├── sessions.js       (saveSession, getSessions)
    │   ├── analytics.js      (getSummary, getWeekly, getByExercise, getTrend)
    │   ├── recommendations.js (getPlan, refreshPlan)
    │   └── pose.js           (analyseFrame)
    │
    ├── context/
    │   └── AuthContext.jsx   (user state, login(), logout(), token management)
    │
    ├── hooks/
    │   ├── useAuth.js        (shortcut hook for useContext(AuthContext))
    │   ├── useWebcam.js      (getUserMedia, frame capture, cleanup)
    │   └── usePoseSession.js (interval-based frame sending, rep counting state)
    │
    ├── components/
    │   ├── layout/
    │   │   ├── Navbar.jsx            (top nav with links and logout button)
    │   │   └── ProtectedRoute.jsx    (redirects to / if no token)
    │   ├── ui/
    │   │   ├── MetricCard.jsx        (stat display: label + value + optional delta)
    │   │   ├── AlertBanner.jsx       (success/error/info banner)
    │   │   ├── LoadingSpinner.jsx    (centered spinner)
    │   │   ├── StepProgress.jsx      (step indicator: "Step 2 of 5")
    │   │   └── Button.jsx            (primary/secondary/danger variants)
    │   ├── charts/
    │   │   ├── AccuracyTrendChart.jsx    (line chart)
    │   │   ├── WeeklySessionsChart.jsx   (bar chart)
    │   │   ├── ExerciseBreakdownChart.jsx (horizontal bar)
    │   │   └── AccuracyGauge.jsx         (radial gauge using Recharts RadialBar)
    │   └── workout/
    │       ├── DayCard.jsx           (one day in the weekly plan)
    │       └── ExerciseEntry.jsx     (one exercise row inside a DayCard)
    │
    └── pages/
        ├── Home.jsx           (login + register tabs)
        ├── Onboarding.jsx     (5-step wizard)
        ├── Exercise.jsx       (live webcam session)
        ├── Dashboard.jsx      (analytics and progress)
        └── WorkoutPlan.jsx    (weekly plan calendar)

---

## Detailed implementation requirements per file

### vite.config.js
Configure a dev server proxy so all /api/* requests are forwarded to
http://localhost:8000 with /api stripped from the path. This avoids
CORS issues during development.

### tailwind.config.js
Content paths: ["./index.html", "./src/**/*.{js,jsx}"]
Extend theme with custom colours:
  primary: "#1976D2"
  success: "#388E3C"
  warning: "#F57C00"
  danger:  "#D32F2F"
  surface: "#F5F7FA"

### src/api/client.js
Create an axios instance with baseURL = import.meta.env.VITE_API_BASE_URL
or "http://localhost:8000" as fallback.
Add a request interceptor: read token from localStorage("token"),
if present add Authorization: Bearer {token} header.
Add a response interceptor: if 401 response, remove token from
localStorage and redirect to "/" (window.location.href = "/").

### src/api/auth.js
Implement and export:
  login(username, password) → POST /users/login → returns token string
  register(userData) → POST /users/register → returns user object
  getMe() → GET /users/me → returns user object

### src/context/AuthContext.jsx
Implement AuthProvider with useState for user and token.
On mount, if localStorage has "token", call getMe() to restore user state.
If getMe() throws 401, clear the token.
Provide: user, token, loading, login(token, user), logout()
login() stores token in localStorage and sets state.
logout() removes token from localStorage, clears state, redirects to "/".

### src/hooks/useWebcam.js
Custom hook that:
- Accepts { width: 640, height: 480 } config
- On mount, calls navigator.mediaDevices.getUserMedia({ video: config })
- Attaches the stream to a videoRef
- On unmount, stops all tracks to release the camera
- Returns { videoRef, canvasRef, isReady, error }
isReady is true once the video element fires the "loadedmetadata" event.
canvasRef is an offscreen canvas sized to width x height, used for
frame capture. It does not need to be in the DOM.

### src/hooks/usePoseSession.js
Custom hook that accepts { exercise, sessionId, isRunning }
When isRunning is true, sets up an interval (every 100ms) that:
  1. Draws the current video frame to the offscreen canvas
  2. Calls canvas.toBlob() to get a JPEG blob
  3. Calls api/pose.analyseFrame(blob, exercise, sessionId)
  4. Updates state: angle, state, feedback, repCount, correctReps,
     incorrectReps, accuracy
When isRunning becomes false, clears the interval.
Returns { angle, state, feedback, repCount, correctReps,
          incorrectReps, accuracy, isAnalysing }

### src/pages/Home.jsx
Two tabs: Login and Register.
Use local component state (useState) for form fields.
No React Hook Form needed here — keep it simple.
LOGIN tab:
  username input, password input (type="password"), Login button.
  On submit: call auth.login(username, password).
  Store token in AuthContext via login().
  Call getMe() to get user object.
  Check onboarding status: GET /onboarding/status.
  If onboarding_complete false: navigate("/onboarding").
  If true: navigate("/dashboard").
  On error: show AlertBanner with error message.
REGISTER tab:
  username, email, password, confirm password inputs.
  Validate passwords match before submitting.
  Call auth.register(data).
  On success: switch to Login tab and show success message.
  On error: show AlertBanner.

### src/pages/Onboarding.jsx
5-step wizard. Use useState for currentStep (1-5) and formData (object
accumulating all fields). Use React Hook Form for field validation.

Show StepProgress component at the top of every step.

Step 1 is skipped (account already created) — start at step 2.

Step 2 — Body profile:
  Fields: age (number, 13-100), gender (select, optional),
  height_cm (number, 50-300), weight_kg (number, 20-300),
  fitness_level (radio: Beginner/Intermediate/Advanced).
  Auto-calculate and display BMI live:
    bmi = weight_kg / (height_cm / 100) ** 2
    Show as a MetricCard that updates on every keystroke.
    Show BMI category label below:
      < 18.5 = "Underweight" (blue)
      18.5-24.9 = "Normal weight" (green)
      25-29.9 = "Overweight" (orange)
      >= 30 = "Obese" (red)
    Show disclaimer: "BMI is for reference only and does not affect
    your workout plan."

Step 3 — Workout goal:
  Radio group with these options and descriptions:
    weight_loss:       "Burns calories through varied intensity circuits"
    muscle_gain:       "Progressive overload with compound movements"
    strength_training: "Low rep, high resistance to build raw strength"
    endurance:         "High rep, lower rest to improve stamina"
    general_fitness:   "Balanced mix of strength and cardio"
    flexibility:       "Range of motion and joint mobility focus"
    sports_specific:   "Explosive power for athletic performance"
  Show the description for the selected option in a highlighted info box.

Step 4 — Equipment:
  Radio: "I have equipment" / "Bodyweight only".
  If equipment selected, show a checkbox grid for:
    Dumbbells, Resistance bands, Pull-up bar, Kettlebell,
    Barbell + rack, Bench, Cables/machine, Full gym access.
  Require at least one item checked if "I have equipment" selected.

Step 5 — Availability:
  days_per_week: range slider 1-7, show value as "{n} days per week"
  workout_duration_minutes: select [15, 20, 30, 45, 60, 75, 90]
  preferred_time: select [Early morning (5-8am), Morning (8-11am),
    Midday (11am-2pm), Afternoon (2-5pm), Evening (5-8pm),
    Late evening (8-11pm)]

  Show a profile summary card before the submit button:
    Two-column grid of MetricCard components showing all collected data.

  Submit button label: "Build my plan →"
  On submit: POST /onboarding/complete with all formData.
  On success: navigate("/plan").
  On error: show AlertBanner.

Navigation:
  "Continue →" button advances to next step after validation.
  "← Back" button on steps 3-5 goes back one step.
  All formData persists when navigating back and forward.

### src/pages/Exercise.jsx
Layout: two-column grid (60% / 40%).

Left column:
  Live webcam feed displayed using a <video> element (not canvas).
  An overlay canvas (position: absolute) drawn on top of the video
  to show a skeleton overlay if returned by the API in future.
  Below the video: exercise selector (select element with 5 options:
  Squat, Bicep Curl, Push-up, Dumbbell Fly, Dumbbell Kickback).
  "Start Session" button (green). "Stop Session" button (red).

Right column:
  Three MetricCard components stacked vertically:
    "Reps completed" showing repCount
    "Posture accuracy" showing accuracy as percentage
    "Current state" showing state (Rest / Moving / Complete)
  Below metrics: a feedback text box (light yellow background) showing
  the feedback string from the API response.
  Below feedback: a session log list showing the last 5 feedback
  messages received (so the user can see history).

Webcam logic:
  Use useWebcam hook for camera access.
  Use usePoseSession hook for frame sending and state management.
  isRunning state controlled by Start/Stop buttons.

On session stop:
  Show a modal or inline summary:
    Exercise name, total reps, correct reps, incorrect reps,
    accuracy %, duration in minutes and seconds.
  "Save session" button → POST /sessions/ with session data.
  "Discard" button → clear state without saving.
  After save: show success message and "View Dashboard" link.

### src/pages/Dashboard.jsx
On mount, fetch all four analytics endpoints in parallel using
Promise.all(). Show LoadingSpinner while fetching.

Layout:
  Row 1: Four MetricCard components in a 4-column grid:
    Total sessions, Total reps, Avg accuracy (with % suffix),
    Current streak (with "days" suffix).
  Row 2: Two charts in a 2-column grid:
    Left: AccuracyTrendChart (line chart, full width of its column)
    Right: WeeklySessionsChart (bar chart)
  Row 3: ExerciseBreakdownChart full width.
  Row 4: Two-column grid:
    Left: AccuracyGauge
    Right: Table of last 10 sessions with columns:
      Date, Exercise, Reps, Correct, Accuracy, Duration

Table styling: alternating row background, sticky header,
overflow-y scroll if more than 10 rows.

### src/pages/WorkoutPlan.jsx
On mount, GET /recommendations/plan. Show LoadingSpinner while fetching.

Header: "Your workout plan — week of {week_start_date}"
Subheader: "Matched to your profile" or "AI-generated plan" based on
  plan.generated_by field.
"Refresh plan" button in top right → POST /recommendations/plan/refresh
  → show LoadingSpinner while refreshing → update displayed plan.

Day layout:
  7 DayCard components in a responsive grid:
    Mobile: 1 column
    Tablet: 2 columns
    Desktop: 4 columns row 1 (Mon-Thu), 3 columns row 2 (Fri-Sun)
  Highlight today's DayCard with a coloured border (primary blue).

DayCard component:
  Header: day name (bold), "Rest day" or workout icon.
  If is_rest: grey background, muted "Rest & recover" text.
  If workout: white background, list of ExerciseEntry components.

ExerciseEntry component:
  Exercise name (bold), "3 sets × 10 reps" text, form cue in muted italic.

---

## Components specification

### MetricCard.jsx
Props: label (string), value (string|number), delta (string, optional),
       colour (optional: "success"|"warning"|"danger"|"default")
Renders a card with light grey background, label in small muted text
above, value in large bold text, optional delta in small coloured text.

### AlertBanner.jsx
Props: type ("success"|"error"|"info"), message (string), onDismiss (fn)
Renders a coloured banner with an icon and dismiss button.
success: green background. error: red. info: blue.

### StepProgress.jsx
Props: currentStep (number), totalSteps (number), stepName (string)
Renders: "Step {n} of {totalSteps} — {stepName}" text above a
progress bar (div with width = (currentStep-1)/(totalSteps-1) * 100%).

### Button.jsx
Props: variant ("primary"|"secondary"|"danger"), children, onClick,
       disabled, loading (bool)
When loading=true, show a small inline spinner and disable the button.

### AccuracyTrendChart.jsx
Uses Recharts LineChart.
Props: data (array of {session_num, accuracy})
Renders a line chart with:
  XAxis: session_num, label "Session"
  YAxis: 0-100, label "Accuracy (%)"
  ReferenceLine at y=80 with label "Target" in dashed stroke
  Line: dataKey="accuracy", stroke="#1976D2", dot=false
  Tooltip showing "Session {n}: {accuracy}%"

### WeeklySessionsChart.jsx
Uses Recharts BarChart.
Props: data (array of {date, session_count, avg_accuracy})
Renders bars for session_count, coloured by avg_accuracy:
  >= 80: green, 60-79: amber, < 60: red.
  XAxis: date formatted as "Mon 18". Tooltip. Label on each bar.

### ExerciseBreakdownChart.jsx
Uses Recharts BarChart with layout="vertical".
Props: data (array of {exercise, count, avg_accuracy})
Horizontal bars. Each bar shows count, colour-coded by avg_accuracy.
Custom label on the right showing avg_accuracy as "Avg: {n}%".

### AccuracyGauge.jsx
Uses Recharts RadialBarChart.
Props: value (number 0-100)
Single RadialBar from 0 to value. Colour: red if < 60, amber if < 80,
green if >= 80. Large value text in the centre. Label "Avg accuracy".

### DayCard.jsx
Props: dayName (string), plan ({ is_rest, exercises })
Props: isToday (bool) — adds highlight border if true.

### ExerciseEntry.jsx
Props: exercise (string), sets (number), reps (number), notes (string)

---

## Coding standards

- All components: functional components with hooks, no class components
- All props: JSDoc comments showing prop types and descriptions
- All API calls: wrapped in try/catch, errors shown via AlertBanner
- All pages: show LoadingSpinner while data is being fetched
- No inline styles: use only Tailwind classes
- Accessibility: all inputs have associated <label> elements,
  all icon-only buttons have aria-label attributes
- All form submits: disable the submit button while the request is pending
  and show a loading spinner inside the button
- Responsive: all layouts work on mobile (min 375px) and desktop
- Token handling: always read from localStorage, never hardcode

---

## Files to generate

Generate all files listed in the project structure above.
Each file must have:
  - A JSDoc comment at the top describing the file's purpose
  - All imports at the top
  - Complete implementation (not just stubs) for components under 80 lines
  - Detailed TODO comments for complex logic (webcam loop, chart colouring)
  - PropTypes or JSDoc prop documentation on every component

Also generate:
  - package.json with all dependencies and scripts:
      "dev": "vite"
      "build": "vite build"
      "preview": "vite preview"
  - .env.example with VITE_API_BASE_URL=http://localhost:8000

Do NOT generate:
  - Any Streamlit files
  - Any Python files (the backend is already built)
  - Any CSS files (Tailwind only)
  - TypeScript (use plain JavaScript JSX)
```
