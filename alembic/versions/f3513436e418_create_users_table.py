"""create users table

Revision ID: f3513436e418
Revises: None
Create Date: 2026-08-19 13:11:54.184546

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f3513436e418'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("email", sa.String(length=100), nullable=False),
        sa.Column("hashed_password", sa.String(length=200), nullable=False),
        sa.Column("age", sa.Integer(), nullable=True),
        sa.Column("fitness_level", sa.String(length=20), nullable=False),
        sa.Column("goal", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("onboarding_complete", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_username", "users", ["username"], unique=True)

    op.create_table(
        "user_profiles",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("age", sa.Integer(), nullable=False),
        sa.Column("gender", sa.String(length=20), nullable=True),
        sa.Column("height_cm", sa.Float(), nullable=False),
        sa.Column("weight_kg", sa.Float(), nullable=False),
        sa.Column("bmi", sa.Float(), nullable=False),
        sa.Column("fitness_level", sa.String(length=20), nullable=False),
        sa.Column("goal", sa.String(length=50), nullable=False),
        sa.Column("has_equipment", sa.Boolean(), nullable=False),
        sa.Column("equipment_list", sa.JSON(), nullable=True),
        sa.Column("days_per_week", sa.Integer(), nullable=False),
        sa.Column("workout_duration_minutes", sa.Integer(), nullable=False),
        sa.Column("preferred_time", sa.String(length=50), nullable=False),
        sa.Column("onboarding_complete", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )

    op.create_table(
        "exercise_sessions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("exercise_type", sa.String(length=50), nullable=False),
        sa.Column("total_reps", sa.Integer(), nullable=False),
        sa.Column("correct_reps", sa.Integer(), nullable=False),
        sa.Column("incorrect_reps", sa.Integer(), nullable=False),
        sa.Column("posture_accuracy", sa.Float(), nullable=True),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "workout_plans",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("plan_data", sa.JSON(), nullable=False),
        sa.Column("generated_at", sa.DateTime(), nullable=False),
        sa.Column("week_start_date", sa.Date(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "posture_feedback_logs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("session_id", sa.String(length=36), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("feedback_message", sa.String(length=200), nullable=True),
        sa.Column("joint_angle", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(["session_id"], ["exercise_sessions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("posture_feedback_logs")
    op.drop_table("workout_plans")
    op.drop_table("exercise_sessions")
    op.drop_table("user_profiles")
    op.drop_index("ix_users_username", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
