# React Migration Guide
## AI Personal Trainer — Streamlit to React

> Work through this guide **in order**. Each phase builds on the previous one.
> Keep your FastAPI backend running on `localhost:8000` throughout.
> Open the relevant source file alongside this guide as you work.

---

## Before you start — checklist

- [ ] Node.js LTS installed (`node --version` prints v20.x or higher)
- [ ] npm installed (`npm --version` prints 10.x or higher)
- [ ] FastAPI backend runs without errors on `localhost:8000`
- [ ] PostgreSQL is running and all tables exist (`alembic upgrade head` done)
- [ ] You can reach `http://localhost:8000/docs` in the browser
- [ ] Git is set up — commit your current Streamlit code before touching anything

```bash
# Save your Streamlit work before starting
git add .
git commit -m "chore: save Streamlit frontend before React migration"
git checkout -b feature/react-frontend
```

---

## Phase 1 — Project setup and tooling

### Step 1 — Back up and remove the Streamlit frontend

```bash
# From your project root (ai-personal-trainer/)
mv frontend frontend_streamlit_backup
```

Do not delete it yet. Keep it as a reference while you rebuild.

---

### Step 2 — Scaffold the React project with Vite

```bash
npm create vite@latest frontend -- --template react
cd frontend
```

You will see this structure created automatically:

```
frontend/
├── index.html
├── vite.config.js
├── package.json
└── src/
    ├── main.jsx
    ├── App.jsx
    └── App.css
```

---

### Step 3 — Install all dependencies

```bash
cd frontend

npm install react-router-dom axios recharts lucide-react react-hook-form

npm install -D tailwindcss postcss autoprefixer

npx tailwindcss init -p
```

Your `package.json` dependencies section should now include:

```json
{
  "dependencies": {
    "react": "^18.x",
    "react-dom": "^18.x",
    "react-router-dom": "^6.x",
    "axios": "^1.x",
    "recharts": "^2.x",
    "lucide-react": "^0.x",
    "react-hook-form": "^7.x"
  },
  "devDependencies": {
    "tailwindcss": "^3.x",
    "postcss": "^8.x",
    "autoprefixer": "^10.x",
    "vite": "^5.x",
    "@vitejs/plugin-react": "^4.x"
  }
}
```

---

### Step 4 — Configure Tailwind CSS

Open `frontend/tailwind.config.js` and replace its contents with:

```js
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary:  "#1976D2",
        success:  "#388E3C",
        warning:  "#F57C00",
        danger:   "#D32F2F",
        surface:  "#F5F7FA",
      }
    },
  },
  plugins: [],
}
```

Open `frontend/src/index.css` and replace its entire contents with:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

Delete `frontend/src/App.css` — you will not use it.

---

### Step 5 — Configure the Vite dev server proxy

Open `frontend/vite.config.js` and replace its contents with:

```js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})
```

This means every call to `/api/users/login` in React automatically
hits `http://localhost:8000/users/login`. No CORS issues in development.

---

### Step 6 — Create the environment file

Create `frontend/.env`:

```
VITE_API_BASE_URL=http://localhost:8000
```

Create `frontend/.env.example` (safe to commit):

```
VITE_API_BASE_URL=http://localhost:8000
```

Add `.env` to `frontend/.gitignore`:

```
# existing entries...
.env
```

---

### Step 7 — Verify the setup runs

```bash
cd frontend
npm run dev
```

Open `http://localhost:5173` in the browser.
You should see the default Vite + React welcome page.
If you see it, Phase 1 is complete. ✓

---

## Phase 2 — API layer and authentication

### Step 8 — Create the folder structure

```bash
cd frontend/src
mkdir -p api context hooks components/layout components/ui components/charts components/workout pages
```

---

### Step 9 — Build the Axios client (`src/api/client.js`)

Create `frontend/src/api/client.js`:

```js
/**
 * Axios instance with JWT interceptor.
 * All API calls go through this client.
 * Automatically attaches the Bearer token from localStorage.
 */
import axios from 'axios'

const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
})

// Attach JWT token to every request
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle 401 globally — clear token and redirect to login
client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/'
    }
    return Promise.reject(error)
  }
)

export default client
```

---

### Step 10 — Build all API modules

Create each file below. These replace all the `requests.get/post` calls
that were scattered across your Streamlit pages.

**`src/api/auth.js`**
```js
import client from './client'

export const login = (username, password) =>
  client.post('/users/login', { username, password }).then(r => r.data)

export const register = (data) =>
  client.post('/users/register', data).then(r => r.data)

export const getMe = () =>
  client.get('/users/me').then(r => r.data)
```

**`src/api/onboarding.js`**
```js
import client from './client'

export const completeOnboarding = (data) =>
  client.post('/onboarding/complete', data).then(r => r.data)

export const getOnboardingStatus = () =>
  client.get('/onboarding/status').then(r => r.data)

export const getOnboardingProfile = () =>
  client.get('/onboarding/profile').then(r => r.data)
```

**`src/api/sessions.js`**
```js
import client from './client'

export const saveSession = (data) =>
  client.post('/sessions/', data).then(r => r.data)

export const getSessions = (params) =>
  client.get('/sessions/', { params }).then(r => r.data)
```

**`src/api/analytics.js`**
```js
import client from './client'

export const getSummary       = () => client.get('/analytics/summary').then(r => r.data)
export const getWeekly        = () => client.get('/analytics/weekly').then(r => r.data)
export const getByExercise    = () => client.get('/analytics/by-exercise').then(r => r.data)
export const getAccuracyTrend = () => client.get('/analytics/accuracy-trend').then(r => r.data)
```

**`src/api/recommendations.js`**
```js
import client from './client'

export const getPlan    = () => client.get('/recommendations/plan').then(r => r.data)
export const refreshPlan = () => client.post('/recommendations/plan/refresh').then(r => r.data)
```

**`src/api/pose.js`**
```js
import client from './client'

export const analyseFrame = (blob, exercise, sessionId) => {
  const form = new FormData()
  form.append('file', blob, 'frame.jpg')
  form.append('exercise', exercise)
  form.append('session_id', sessionId)
  return client.post('/pose/analyse-frame', form).then(r => r.data)
}
```

---

### Step 11 — Build the Auth context (`src/context/AuthContext.jsx`)

```jsx
/**
 * AuthContext — provides user state and login/logout to the entire app.
 * Equivalent to st.session_state["token"] and st.session_state["user"].
 */
import { createContext, useContext, useState, useEffect } from 'react'
import { getMe } from '../api/auth'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser]       = useState(null)
  const [token, setToken]     = useState(localStorage.getItem('token'))
  const [loading, setLoading] = useState(!!localStorage.getItem('token'))

  // Restore user on page refresh if token exists
  useEffect(() => {
    if (token && !user) {
      getMe()
        .then(setUser)
        .catch(() => { localStorage.removeItem('token'); setToken(null) })
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [])

  const login = (tokenValue, userData) => {
    localStorage.setItem('token', tokenValue)
    setToken(tokenValue)
    setUser(userData)
  }

  const logout = () => {
    localStorage.removeItem('token')
    setToken(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, token, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
```

---

### Step 12 — Build the router (`src/App.jsx`)

```jsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import Home        from './pages/Home'
import Onboarding  from './pages/Onboarding'
import Exercise    from './pages/Exercise'
import Dashboard   from './pages/Dashboard'
import WorkoutPlan from './pages/WorkoutPlan'
import LoadingSpinner from './components/ui/LoadingSpinner'

function ProtectedRoute({ children }) {
  const { token, loading } = useAuth()
  if (loading) return <LoadingSpinner />
  return token ? children : <Navigate to="/" replace />
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/"           element={<Home />} />
          <Route path="/onboarding" element={<ProtectedRoute><Onboarding /></ProtectedRoute>} />
          <Route path="/exercise"   element={<ProtectedRoute><Exercise /></ProtectedRoute>} />
          <Route path="/dashboard"  element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
          <Route path="/plan"       element={<ProtectedRoute><WorkoutPlan /></ProtectedRoute>} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}
```

Update `src/main.jsx`:

```jsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
```

**Checkpoint:** `npm run dev` should still show no errors in the terminal.
The browser will show a blank page (no pages built yet) — that is fine. ✓

---

## Phase 3 — Shared UI components

Build these small reusable components before the pages.
Pages depend on them.

### Step 13 — `src/components/ui/LoadingSpinner.jsx`

```jsx
export default function LoadingSpinner({ message = 'Loading...' }) {
  return (
    <div className="flex flex-col items-center justify-center h-64 gap-4">
      <div className="w-10 h-10 border-4 border-primary border-t-transparent rounded-full animate-spin" />
      <p className="text-gray-500 text-sm">{message}</p>
    </div>
  )
}
```

### Step 14 — `src/components/ui/MetricCard.jsx`

```jsx
export default function MetricCard({ label, value, delta, colour = 'default' }) {
  const colours = {
    success: 'text-success',
    warning: 'text-warning',
    danger:  'text-danger',
    default: 'text-gray-800',
  }
  return (
    <div className="bg-white rounded-xl shadow-sm p-4 border border-gray-100">
      <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">{label}</p>
      <p className={`text-2xl font-bold ${colours[colour]}`}>{value}</p>
      {delta && <p className="text-xs text-gray-400 mt-1">{delta}</p>}
    </div>
  )
}
```

### Step 15 — `src/components/ui/AlertBanner.jsx`

```jsx
import { X } from 'lucide-react'

const styles = {
  success: 'bg-green-50 border-green-400 text-green-800',
  error:   'bg-red-50 border-red-400 text-red-800',
  info:    'bg-blue-50 border-blue-400 text-blue-800',
}

export default function AlertBanner({ type = 'info', message, onDismiss }) {
  return (
    <div className={`flex items-start gap-3 border-l-4 rounded p-3 ${styles[type]}`}>
      <p className="flex-1 text-sm">{message}</p>
      {onDismiss && (
        <button onClick={onDismiss} aria-label="Dismiss" className="mt-0.5 opacity-60 hover:opacity-100">
          <X size={16} />
        </button>
      )}
    </div>
  )
}
```

### Step 16 — `src/components/ui/Button.jsx`

```jsx
const variants = {
  primary:   'bg-primary text-white hover:bg-blue-700',
  secondary: 'bg-gray-100 text-gray-800 hover:bg-gray-200',
  danger:    'bg-danger text-white hover:bg-red-700',
}

export default function Button({ variant = 'primary', children, onClick, disabled, loading }) {
  return (
    <button
      onClick={onClick}
      disabled={disabled || loading}
      className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-sm
        transition-colors disabled:opacity-50 disabled:cursor-not-allowed
        ${variants[variant]}`}
    >
      {loading && (
        <span className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
      )}
      {children}
    </button>
  )
}
```

### Step 17 — `src/components/ui/StepProgress.jsx`

```jsx
export default function StepProgress({ currentStep, totalSteps, stepName }) {
  const pct = ((currentStep - 1) / (totalSteps - 1)) * 100

  return (
    <div className="mb-6">
      <div className="flex justify-between items-center mb-2">
        <p className="text-sm text-gray-500">
          Step <span className="font-semibold text-gray-800">{currentStep}</span> of {totalSteps}
          {stepName && <span className="text-gray-400"> — {stepName}</span>}
        </p>
        <p className="text-xs text-gray-400">{Math.round(pct)}%</p>
      </div>
      <div className="w-full bg-gray-100 rounded-full h-2">
        <div
          className="bg-primary h-2 rounded-full transition-all duration-300"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  )
}
```

### Step 18 — `src/components/layout/Navbar.jsx`

```jsx
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { Dumbbell, LayoutDashboard, CalendarDays, Video, LogOut } from 'lucide-react'

const links = [
  { to: '/exercise',  label: 'Exercise',  icon: Video },
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/plan',      label: 'My Plan',   icon: CalendarDays },
]

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => { logout(); navigate('/') }

  return (
    <nav className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between">
      <Link to="/dashboard" className="flex items-center gap-2 font-bold text-primary text-lg">
        <Dumbbell size={22} />
        AI Trainer
      </Link>

      <div className="flex items-center gap-1">
        {links.map(({ to, label, icon: Icon }) => (
          <Link
            key={to}
            to={to}
            className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm text-gray-600
              hover:bg-surface hover:text-primary transition-colors"
          >
            <Icon size={16} /> {label}
          </Link>
        ))}
      </div>

      <div className="flex items-center gap-3">
        <span className="text-sm text-gray-500">{user?.username}</span>
        <button
          onClick={handleLogout}
          className="flex items-center gap-1 text-sm text-gray-500 hover:text-danger"
          aria-label="Log out"
        >
          <LogOut size={16} /> Logout
        </button>
      </div>
    </nav>
  )
}
```

---

## Phase 4 — Custom hooks and webcam

### Step 19 — `src/hooks/useWebcam.js`

```js
/**
 * Manages webcam access via getUserMedia.
 * Returns refs for the video element and an offscreen canvas.
 */
import { useRef, useState, useEffect } from 'react'

export function useWebcam({ width = 640, height = 480 } = {}) {
  const videoRef  = useRef(null)
  const canvasRef = useRef(document.createElement('canvas'))
  const [isReady, setIsReady] = useState(false)
  const [error,   setError]   = useState(null)

  useEffect(() => {
    canvasRef.current.width  = width
    canvasRef.current.height = height

    navigator.mediaDevices
      .getUserMedia({ video: { width, height, facingMode: 'user' } })
      .then((stream) => {
        if (videoRef.current) {
          videoRef.current.srcObject = stream
          videoRef.current.onloadedmetadata = () => setIsReady(true)
        }
      })
      .catch((err) => setError(err.message))

    return () => {
      if (videoRef.current?.srcObject) {
        videoRef.current.srcObject.getTracks().forEach(t => t.stop())
      }
    }
  }, [width, height])

  return { videoRef, canvasRef, isReady, error }
}
```

### Step 20 — `src/hooks/usePoseSession.js`

```js
/**
 * Sends webcam frames to FastAPI /pose/analyse-frame every 100ms.
 * Manages rep count, accuracy, and feedback state.
 */
import { useRef, useState, useEffect } from 'react'
import { analyseFrame } from '../api/pose'

export function usePoseSession({ videoRef, canvasRef, exercise, sessionId, isRunning }) {
  const intervalRef = useRef(null)

  const [angle,        setAngle]        = useState(0)
  const [state,        setState]        = useState('REST')
  const [feedback,     setFeedback]     = useState('')
  const [repCount,     setRepCount]     = useState(0)
  const [correctReps,  setCorrectReps]  = useState(0)
  const [incorrectReps,setIncorrectReps]= useState(0)
  const [accuracy,     setAccuracy]     = useState(0)
  const [isAnalysing,  setIsAnalysing]  = useState(false)

  useEffect(() => {
    if (!isRunning) {
      clearInterval(intervalRef.current)
      return
    }

    intervalRef.current = setInterval(async () => {
      if (!videoRef.current || !canvasRef.current) return

      const canvas = canvasRef.current
      const ctx    = canvas.getContext('2d')
      ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height)

      canvas.toBlob(async (blob) => {
        if (!blob) return
        setIsAnalysing(true)
        try {
          const data = await analyseFrame(blob, exercise, sessionId)
          setAngle(data.angle ?? 0)
          setState(data.state ?? 'REST')
          setFeedback(data.feedback ?? '')
          setRepCount(data.rep_count ?? 0)
          setCorrectReps(data.correct_reps ?? 0)
          setIncorrectReps(data.incorrect_reps ?? 0)
          setAccuracy(data.rep_count > 0
            ? Math.round((data.correct_reps / data.rep_count) * 100)
            : 0)
        } catch (e) {
          // Silently skip failed frames
        } finally {
          setIsAnalysing(false)
        }
      }, 'image/jpeg', 0.8)
    }, 100)

    return () => clearInterval(intervalRef.current)
  }, [isRunning, exercise, sessionId])

  const reset = () => {
    setAngle(0); setState('REST'); setFeedback('')
    setRepCount(0); setCorrectReps(0); setIncorrectReps(0); setAccuracy(0)
  }

  return { angle, state, feedback, repCount, correctReps, incorrectReps, accuracy, isAnalysing, reset }
}
```

---

## Phase 5 — Pages

### Step 21 — Build pages using the Copilot prompt

At this point open `COPILOT_REACT_MIGRATION_PROMPT.md`, copy the
prompt, and paste it into Copilot Chat. Copilot will generate full
implementations of all five pages based on the detailed spec.

Then work through each page manually using these checklists:

#### `Home.jsx` checklist
- [ ] Login tab: username + password inputs, Login button
- [ ] Login calls `auth.login()` then `getMe()` then checks onboarding status
- [ ] Routes to `/onboarding` if not complete, `/dashboard` if complete
- [ ] Register tab: username, email, password, confirm password
- [ ] Password match validation before submit
- [ ] Both tabs show AlertBanner on error
- [ ] Submit button shows loading spinner while request is in flight

#### `Onboarding.jsx` checklist
- [ ] StepProgress bar at top of every step
- [ ] Step 2: BMI auto-calculates and updates on every keystroke
- [ ] Step 2: BMI category label changes colour correctly
- [ ] Step 3: goal description shows in info box when option selected
- [ ] Step 4: equipment checklist only shows when "I have equipment" selected
- [ ] Step 5: summary card shows all collected data from formData
- [ ] Back button preserves all previously entered values
- [ ] Submit POSTs to `/onboarding/complete` and navigates to `/plan`

#### `Exercise.jsx` checklist
- [ ] Webcam feed visible in left column via `<video>` element
- [ ] Exercise selector works and is disabled while session is running
- [ ] Start Session generates a new UUID for sessionId
- [ ] Frames are sent every 100ms while running
- [ ] Right column metrics update in real time
- [ ] Stop Session shows session summary modal
- [ ] Save session POSTs to `/sessions/` and shows success

#### `Dashboard.jsx` checklist
- [ ] All four analytics endpoints fetched in parallel with `Promise.all`
- [ ] LoadingSpinner shown while fetching
- [ ] Four MetricCard components in top row
- [ ] All four charts render with correct data
- [ ] Last 10 sessions table with alternating row colours

#### `WorkoutPlan.jsx` checklist
- [ ] Plan loaded on mount
- [ ] Today's day card has blue border highlight
- [ ] Rest days show grey styling
- [ ] Workout days show exercise entries with sets/reps/notes
- [ ] Refresh plan button works and updates the displayed plan

---

## Phase 6 — Backend addition for pose endpoint

### Step 22 — Add `/pose/analyse-frame` to FastAPI

Create `backend/routers/pose.py`:

```python
"""
Pose analysis endpoint.
Accepts a JPEG video frame and returns joint angles, state,
rep count, and feedback for the specified exercise.
"""
from fastapi import APIRouter, UploadFile, Form, Depends
import numpy as np
import cv2
from pose_engine.detector import PoseDetector
from pose_engine.angle_utils import get_landmark_coords, calculate_angle
from pose_engine.exercises.squat import Squat
from pose_engine.exercises.bicep_curl import BicepCurl
from pose_engine.exercises.pushup import Pushup
from pose_engine.exercises.dumbbell_fly import DumbbellFly
from pose_engine.exercises.kickback import Kickback
from backend.dependencies import get_current_user

router = APIRouter(prefix="/pose", tags=["pose"])

# Module-level detector shared across requests
detector = PoseDetector()

EXERCISES = {
    "Squat":          Squat(),
    "Bicep Curl":     BicepCurl(),
    "Push-up":        Pushup(),
    "Dumbbell Fly":   DumbbellFly(),
    "Dumbbell Kickback": Kickback(),
}

# Per-session state machines stored in memory
# In production this would move to Redis
_session_machines = {}

@router.post("/analyse-frame")
async def analyse_frame(
    file: UploadFile,
    exercise: str = Form(...),
    session_id: str = Form(...),
    current_user=Depends(get_current_user),
):
    # Decode the uploaded JPEG frame
    contents = await file.read()
    nparr    = np.frombuffer(contents, np.uint8)
    frame    = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Run pose detection
    results = detector.detect(frame_rgb)
    if results.pose_landmarks is None:
        return {"angle": 0, "state": "REST", "rep_completed": False,
                "correct": False, "feedback": "No person detected",
                "rep_count": 0, "correct_reps": 0, "incorrect_reps": 0}

    # Get or create state machine for this session
    from pose_engine.state_machine import ExerciseStateMachine
    if session_id not in _session_machines:
        _session_machines[session_id] = ExerciseStateMachine()
    sm = _session_machines[session_id]

    ex = EXERCISES.get(exercise, Squat())
    landmarks = results.pose_landmarks.landmark
    ids = ex.get_required_landmarks()
    a = get_landmark_coords(landmarks, ids[0], frame.shape)
    b = get_landmark_coords(landmarks, ids[1], frame.shape)
    c = get_landmark_coords(landmarks, ids[2], frame.shape)
    angle = calculate_angle(a, b, c)

    state, rep_done = sm.update(angle, ex.get_angle_thresholds())
    feedback = ex.get_feedback(angle, state)

    return {
        "angle":        round(angle, 1),
        "state":        state,
        "rep_completed": rep_done,
        "correct":      rep_done,
        "feedback":     feedback,
        "rep_count":    sm.correct_count + sm.incorrect_count,
        "correct_reps": sm.correct_count,
        "incorrect_reps": sm.incorrect_count,
    }
```

Register in `backend/main.py`:

```python
from backend.routers import pose
app.include_router(pose.router)
```

---

## Phase 7 — Final cleanup

### Step 23 — Update CORS in FastAPI

Open `backend/main.py` and update CORS to include the React dev URL:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # React dev server
        "http://localhost:4173",   # React preview
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### Step 24 — Final end-to-end test

Run both servers simultaneously:

```bash
# Terminal 1 — FastAPI backend
cd ai-personal-trainer
uvicorn backend.main:app --reload --port 8000

# Terminal 2 — React frontend
cd ai-personal-trainer/frontend
npm run dev
```

Work through this full test sequence:

- [ ] Register a new user at `localhost:5173`
- [ ] Onboarding wizard completes all 5 steps
- [ ] Workout plan page shows matched static plan
- [ ] Exercise page opens webcam without errors
- [ ] Starting a session sends frames and shows rep count updating
- [ ] Stopping and saving session works
- [ ] Dashboard shows updated session count and accuracy

---

### Step 25 — Remove Streamlit

Once every checklist above passes:

```bash
# Remove the Streamlit backup
rm -rf frontend_streamlit_backup

# Remove streamlit from Python dependencies
# Open requirements.txt and delete the streamlit line

# Verify backend still runs cleanly
uvicorn backend.main:app --reload --port 8000
```

---

### Step 26 — Update project documentation

Update your `README.md` run instructions:

```markdown
## Running the project

### Backend
```bash
uvicorn backend.main:app --reload --port 8000
```
API docs: http://localhost:8000/docs

### Frontend
```bash
cd frontend
npm run dev
```
Open: http://localhost:5173
```

Commit everything:

```bash
git add .
git commit -m "feat: migrate frontend from Streamlit to React"
git push origin feature/react-frontend
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `npm run dev` fails with module not found | Run `npm install` inside the `frontend/` folder |
| API calls return 401 immediately | Check `localStorage.getItem("token")` in browser DevTools console |
| Webcam shows "Permission denied" | Browser needs HTTPS or localhost — ensure you are on `localhost:5173` not `127.0.0.1` |
| CORS error in browser console | Confirm `localhost:5173` is in the FastAPI CORS allow_origins list |
| Blank page after login | Check browser console for React router errors — ensure all page imports are correct |
| Frames not sending | Check that `isRunning` state is `true` and `videoRef.current` is not null |
| Charts not rendering | Ensure analytics endpoints return arrays, not null — check FastAPI logs |
| BMI not updating live | Ensure height and weight are controlled inputs using `useState` not `defaultValue` |
