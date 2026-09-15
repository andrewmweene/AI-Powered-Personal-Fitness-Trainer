# Copilot Prompt — Register Deployment Configuration
## Supabase + Render + Vercel + Alembic Migrations

> **How to use:**
> 1. Open GitHub Copilot Chat in VS Code (`Ctrl+Shift+I`)
> 2. Paste the entire prompt block below and send it
> 3. Copilot will create or modify every file listed
> 4. After Copilot generates the files, follow the
>    POST-GENERATION CHECKLIST at the bottom of this file

---

## Prompt — paste into Copilot Chat

```
I am configuring my AI Personal Trainer project for deployment.
The three-part hosting setup is:
  - React frontend  → Vercel       (vercel.com, free tier)
  - FastAPI backend → Render       (render.com, free tier)
  - Database        → Supabase     (supabase.com, free tier, already configured)

Please create or modify every file listed below to register this
deployment configuration into the codebase. Do not change any
business logic, models, routes, or React components — only
configuration and infrastructure files.

---

## 1. Root-level files to CREATE

### `render.yaml`  (Render deployment manifest — project root)

Create this file at the project root (same level as requirements.txt).
It tells Render how to build and start the FastAPI backend.

Content:
```yaml
services:
  - type: web
    name: ai-trainer-backend
    runtime: python
    region: oregon
    plan: free
    buildCommand: "pip install -r requirements.txt"
    startCommand: "uvicorn backend.main:app --host 0.0.0.0 --port $PORT"
    healthCheckPath: /health
    envVars:
      - key: DATABASE_URL
        sync: false
      - key: SECRET_KEY
        sync: false
      - key: ALGORITHM
        value: HS256
      - key: ACCESS_TOKEN_EXPIRE_MINUTES
        value: "1440"
      - key: GEMINI_API_KEY
        sync: false
      - key: ENVIRONMENT
        value: production
      - key: ALLOWED_ORIGINS
        sync: false
```

### `vercel.json`  (Vercel deployment config — inside frontend/ folder)

Create this file inside the frontend/ folder.
It tells Vercel the build settings for the React/Vite app.

Content:
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "installCommand": "npm install",
  "framework": "vite",
  "rewrites": [
    { "source": "/(.*)", "destination": "/" }
  ]
}
```

The rewrites entry is critical — it makes React Router work correctly
on Vercel so that refreshing any page (e.g. /dashboard) does not 404.

### `.env.example`  (project root — safe to commit, no real secrets)

Create or replace this file with all environment variables the project
needs, with placeholder values and comments explaining each one:

```
# =============================================
# AI Personal Trainer — Environment Variables
# Copy this file to .env and fill in real values
# NEVER commit .env to git
# =============================================

# --- Database (Supabase PostgreSQL) ---
# Get this from: Supabase → Project Settings → Database → URI tab
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.xxxxxxxxxxxx.supabase.co:5432/postgres

# --- JWT Authentication ---
# Generate with: openssl rand -hex 32
SECRET_KEY=your-secret-key-minimum-32-characters-long
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# --- Google Gemini API ---
# Get this from: aistudio.google.com → Get API key
GEMINI_API_KEY=your-gemini-api-key-here

# --- CORS (comma-separated list of allowed frontend origins) ---
# Local development:
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:4173
# Production (add your Vercel URL here after deploying):
# ALLOWED_ORIGINS=http://localhost:5173,https://your-app.vercel.app

# --- Environment ---
ENVIRONMENT=development
# Set to "production" on Render
```

### `frontend/.env.example`  (inside frontend/ folder)

```
# React frontend environment variables
# Copy to frontend/.env for local development
# Set these in Vercel dashboard for production

# URL of the FastAPI backend
# Local development:
VITE_API_BASE_URL=http://localhost:8000
# Production (your Render URL):
# VITE_API_BASE_URL=https://ai-trainer-backend.onrender.com
```

---

## 2. Files to MODIFY

### `backend/main.py` — update CORS middleware

Find the existing CORSMiddleware configuration and replace it with a
dynamic version that reads allowed origins from the ALLOWED_ORIGINS
environment variable. This means you only change the env var to update
CORS — you never touch the code.

Replace the existing CORS middleware block with:

```python
import os
from fastapi.middleware.cors import CORSMiddleware

# Read allowed origins from environment variable
# Falls back to localhost only if env var is not set
_origins_env = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:4173"
)
allowed_origins = [o.strip() for o in _origins_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Also add or verify this health check endpoint exists in main.py.
Render uses it to confirm the service is running:

```python
@app.get("/health", tags=["health"])
def health_check():
    """Health check endpoint used by Render to verify the service is up."""
    return {"status": "ok", "environment": os.getenv("ENVIRONMENT", "development")}
```

### `backend/database.py` — add SSL support for Supabase

Supabase requires SSL. Update the create_engine call to add SSL args
when running in production:

```python
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Supabase (and most hosted PostgreSQL) requires SSL in production
connect_args = {}
if os.getenv("ENVIRONMENT") == "production":
    connect_args = {"sslmode": "require"}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,      # test connections before using them
    pool_recycle=300,        # recycle connections every 5 minutes
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """FastAPI dependency that yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### `alembic/env.py` — connect Alembic to Supabase via DATABASE_URL

Replace the contents of alembic/env.py with a version that:
  - Reads DATABASE_URL from the .env file using python-dotenv
  - Imports all SQLAlchemy models so Alembic can detect them
  - Sets target_metadata correctly for autogenerate to work
  - Handles both online (apply migrations) and offline (generate SQL) modes

```python
"""Alembic environment configuration.

Reads DATABASE_URL from the .env file and connects to the database
(Supabase in production, local PostgreSQL in development) to apply
or generate migrations.
"""
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Import Base and ALL models so Alembic can detect schema changes
from backend.database import Base
from backend.models import (       # noqa: F401  (imports needed for autogenerate)
    User,
    UserProfile,
    ExerciseSession,
    WorkoutPlan,
    PostureFeedbackLog,
)

# Alembic Config object
config = context.config

# Override the sqlalchemy.url from alembic.ini with the one from .env
config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))

# Set up Python logging from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# The metadata object for autogenerate support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode — generates SQL without a connection."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode — connects and applies changes."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,        # detect column type changes
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### `alembic.ini` — point sqlalchemy.url at a placeholder

The actual URL is injected by env.py from the .env file.
Find the line `sqlalchemy.url = ...` and replace it with:

```ini
sqlalchemy.url = %(DATABASE_URL)s
```

This prevents the real database URL from ever being stored in alembic.ini,
which is committed to git.

### `.gitignore` (project root) — ensure secrets are never committed

Add or verify these entries exist:

```
# Environment secrets — NEVER commit
.env
frontend/.env
*.env.local

# Python
__pycache__/
*.pyc
*.pyo
.venv/
venv/
env/
*.egg-info/

# Node
frontend/node_modules/
frontend/dist/
frontend/.vercel/

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/settings.json
.idea/
```

### `requirements.txt` — ensure all deployment dependencies are present

Make sure these packages are in requirements.txt (add any that are missing).
These are required for Render to build successfully:

```
# Core framework
fastapi>=0.110.0
uvicorn[standard]>=0.27.0

# Database
sqlalchemy>=2.0.0
alembic>=1.13.0
psycopg2-binary>=2.9.9

# Auth
python-jose[cryptography]>=3.3.0
bcrypt>=4.1.2
passlib>=1.7.4

# Validation
pydantic[email]>=2.6.0
python-multipart>=0.0.9

# Environment
python-dotenv>=1.0.0

# Computer vision (pose engine)
mediapipe>=0.10.0
opencv-python-headless>=4.8.0
numpy>=1.26.0

# ML and data
scikit-learn>=1.4.0
pandas>=2.2.0

# AI plan generation
google-generativeai>=0.5.0

# HTTP client (for internal calls if needed)
httpx>=0.27.0
```

IMPORTANT: Use opencv-python-headless (not opencv-python) on Render.
The headless version does not require a display server, which Render
does not have. opencv-python will fail to install on Render.

### `frontend/vite.config.js` — update proxy for both local and production

Replace the contents with a version that:
  - Uses the proxy in development (when VITE_API_BASE_URL is localhost)
  - Does NOT use the proxy in production (Vercel calls Render directly)

```js
import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')

  const isDev = mode === 'development'
  const apiBase = env.VITE_API_BASE_URL || 'http://localhost:8000'

  return {
    plugins: [react()],
    server: {
      port: 5173,
      proxy: isDev ? {
        '/api': {
          target: apiBase,
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, ''),
        },
      } : {},
    },
    build: {
      outDir: 'dist',
      sourcemap: false,
    },
  }
})
```

### `frontend/src/api/client.js` — use environment variable for base URL

Update the axios baseURL to use the Vite environment variable so it
correctly points at localhost in development and the Render URL in
production:

```js
import axios from 'axios'

// In development: proxy forwards /api/* to localhost:8000
// In production: calls Render backend directly
const BASE_URL = import.meta.env.PROD
  ? (import.meta.env.VITE_API_BASE_URL || '')
  : '/api'

const client = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,   // 15 second timeout — accounts for Render cold start
})

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/'
    }
    // Surface a user-friendly message for timeout (Render cold start)
    if (error.code === 'ECONNABORTED') {
      error.message = 'The server is waking up — please try again in 30 seconds.'
    }
    return Promise.reject(error)
  }
)

export default client
```

Note the 15-second timeout. Render's free tier can take up to 30 seconds
to wake from sleep. The error message in the interceptor tells the user
what is happening instead of showing a generic network error.

---

## 3. Files to CREATE (infrastructure and migrations)

### `alembic/versions/001_create_users_table.py`

Create this Alembic migration file manually (do not use autogenerate
for this one — write it explicitly so it is version-controlled clearly).

```python
"""create users table

Revision ID: 001
Revises:
Create Date: 2026-08-23
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id',                  postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('username',            sa.String(50),  nullable=False),
        sa.Column('email',               sa.String(100), nullable=False),
        sa.Column('hashed_password',     sa.String(200), nullable=False),
        sa.Column('onboarding_complete', sa.Boolean(),   nullable=True,  server_default='false'),
        sa.Column('created_at',          sa.DateTime(),  nullable=True,  server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email',    name='uq_users_email'),
        sa.UniqueConstraint('username', name='uq_users_username'),
    )
    op.create_index('ix_users_email',    'users', ['email'],    unique=True)
    op.create_index('ix_users_username', 'users', ['username'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_users_username', table_name='users')
    op.drop_index('ix_users_email',    table_name='users')
    op.drop_table('users')
```

### `alembic/versions/002_create_user_profiles_table.py`

```python
"""create user_profiles table

Revision ID: 002
Revises: 001
Create Date: 2026-08-23
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'user_profiles',
        sa.Column('id',                      postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id',                 postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('age',                     sa.Integer(),  nullable=False),
        sa.Column('gender',                  sa.String(30), nullable=True),
        sa.Column('height_cm',               sa.Float(),    nullable=False),
        sa.Column('weight_kg',               sa.Float(),    nullable=False),
        sa.Column('bmi',                     sa.Float(),    nullable=False),
        sa.Column('fitness_level',           sa.String(20), nullable=False),
        sa.Column('goal',                    sa.String(30), nullable=False),
        sa.Column('has_equipment',           sa.Boolean(),  nullable=False, server_default='false'),
        sa.Column('equipment_list',          postgresql.JSON(), nullable=True),
        sa.Column('days_per_week',           sa.Integer(),  nullable=False),
        sa.Column('workout_duration_minutes',sa.Integer(),  nullable=False),
        sa.Column('preferred_time',          sa.String(50), nullable=False),
        sa.Column('onboarding_complete',     sa.Boolean(),  nullable=True, server_default='false'),
        sa.Column('created_at',              sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.Column('updated_at',              sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_user_profiles_user_id', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', name='uq_user_profiles_user_id'),
    )
    op.create_index('ix_user_profiles_user_id', 'user_profiles', ['user_id'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_user_profiles_user_id', table_name='user_profiles')
    op.drop_table('user_profiles')
```

### `alembic/versions/003_create_exercise_sessions_and_workout_plans.py`

```python
"""create exercise_sessions and workout_plans tables

Revision ID: 003
Revises: 002
Create Date: 2026-08-23
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'exercise_sessions',
        sa.Column('id',               postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id',          postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('exercise_type',    sa.String(50),  nullable=False),
        sa.Column('total_reps',       sa.Integer(),   nullable=True, server_default='0'),
        sa.Column('correct_reps',     sa.Integer(),   nullable=True, server_default='0'),
        sa.Column('incorrect_reps',   sa.Integer(),   nullable=True, server_default='0'),
        sa.Column('posture_accuracy', sa.Float(),     nullable=True),
        sa.Column('duration_seconds', sa.Integer(),   nullable=True),
        sa.Column('created_at',       sa.DateTime(),  nullable=True, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_exercise_sessions_user_id', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_exercise_sessions_user_id',    'exercise_sessions', ['user_id'])
    op.create_index('ix_exercise_sessions_created_at', 'exercise_sessions', ['created_at'])

    op.create_table(
        'workout_plans',
        sa.Column('id',              postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id',         postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('plan_data',       postgresql.JSON(), nullable=False),
        sa.Column('generated_at',    sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.Column('week_start_date', sa.Date(),     nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_workout_plans_user_id', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_workout_plans_user_id',        'workout_plans', ['user_id'])
    op.create_index('ix_workout_plans_week_start_date','workout_plans', ['week_start_date'])


def downgrade() -> None:
    op.drop_index('ix_workout_plans_week_start_date', table_name='workout_plans')
    op.drop_index('ix_workout_plans_user_id',         table_name='workout_plans')
    op.drop_table('workout_plans')
    op.drop_index('ix_exercise_sessions_created_at',  table_name='exercise_sessions')
    op.drop_index('ix_exercise_sessions_user_id',     table_name='exercise_sessions')
    op.drop_table('exercise_sessions')
```

### `alembic/versions/004_create_posture_feedback_logs.py`

```python
"""create posture_feedback_logs table

Revision ID: 004
Revises: 003
Create Date: 2026-08-23
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'posture_feedback_logs',
        sa.Column('id',               postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_id',       postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('timestamp',        sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.Column('feedback_message', sa.String(200), nullable=True),
        sa.Column('joint_angle',      sa.Float(),     nullable=True),
        sa.ForeignKeyConstraint(
            ['session_id'], ['exercise_sessions.id'],
            name='fk_posture_feedback_logs_session_id',
            ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_posture_feedback_logs_session_id', 'posture_feedback_logs', ['session_id'])


def downgrade() -> None:
    op.drop_index('ix_posture_feedback_logs_session_id', table_name='posture_feedback_logs')
    op.drop_table('posture_feedback_logs')
```

---

## 4. README.md — update with deployment and run instructions

Find the existing README.md at the project root and add or replace the
"Running the project" and "Deployment" sections with:

```markdown
## Running locally

### Prerequisites
- Python 3.11+
- Node.js v20+
- A Supabase project (free at supabase.com)
- Copy `.env.example` to `.env` and fill in your values
- Copy `frontend/.env.example` to `frontend/.env` and fill in your values

### 1. Install Python dependencies
pip install -r requirements.txt

### 2. Run database migrations (pushes tables to Supabase)
alembic upgrade head

### 3. Start the FastAPI backend
uvicorn backend.main:app --reload --port 8000
API docs available at: http://localhost:8000/docs

### 4. Start the React frontend (new terminal)
cd frontend
npm install
npm run dev
Open: http://localhost:5173

---

## Deployment

| Part             | Platform  | URL pattern                          |
|------------------|-----------|--------------------------------------|
| React frontend   | Vercel    | https://your-app.vercel.app          |
| FastAPI backend  | Render    | https://ai-trainer-backend.onrender.com |
| Database         | Supabase  | Managed PostgreSQL (no public URL)   |

### Deploy backend to Render
1. Push code to GitHub
2. Connect repo to Render (render.com → New Web Service)
3. Add environment variables in Render dashboard:
   DATABASE_URL, SECRET_KEY, GEMINI_API_KEY, ALLOWED_ORIGINS
4. Render auto-deploys on every git push to main

### Deploy frontend to Vercel
1. Connect repo to Vercel (vercel.com → Add New Project)
2. Set root directory to: frontend
3. Add environment variable in Vercel dashboard:
   VITE_API_BASE_URL = https://ai-trainer-backend.onrender.com
4. Vercel auto-deploys on every git push to main

### Run migrations against Supabase
alembic upgrade head
(run from your local machine — DATABASE_URL in .env points to Supabase)
```

---

## Coding standards for this task

- Do not modify any Python models, routes, or business logic
- Do not modify any React components or pages
- Do not change any existing function signatures
- Only create or modify the configuration files listed above
- Every file must have a comment at the top explaining its purpose
- All secret values must come from environment variables — never hardcoded
- The .gitignore must ensure .env files are never committed
```

---

## POST-GENERATION CHECKLIST
## Work through this after Copilot generates the files

- [ ] `.env` exists at project root with your real Supabase DATABASE_URL filled in
- [ ] `frontend/.env` exists with VITE_API_BASE_URL=http://localhost:8000
- [ ] `.gitignore` includes `.env` and `frontend/.env`
- [ ] Run: `alembic upgrade head` — should print 4 migration steps with no errors
- [ ] Check Supabase Table Editor — all 5 tables visible
- [ ] Run: `uvicorn backend.main:app --reload --port 8000`
- [ ] Open: `http://localhost:8000/health` — should return `{"status":"ok"}`
- [ ] Open: `http://localhost:8000/docs` — FastAPI docs load correctly
- [ ] Run: `cd frontend && npm run dev`
- [ ] Open: `http://localhost:5173` — React app loads correctly
- [ ] Commit everything: `git add . && git commit -m "chore: add deployment configuration"`
- [ ] Push to GitHub: `git push origin main`
- [ ] Connect repo to Render — add env vars in Render dashboard
- [ ] Connect repo to Vercel — set root directory to frontend, add VITE_API_BASE_URL
- [ ] Test live: visit your Vercel URL and confirm the app loads
- [ ] Test health: visit https://your-render-app.onrender.com/health
```
