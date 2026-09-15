from backend.demo import ensure_demo_user
from backend.database import SessionLocal
from backend.models import User


def test_ensure_demo_user_creates_default_account() -> None:
    ensure_demo_user()

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == "testuser").first()
        assert user is not None
        assert user.email == "test@example.com"
        assert user.onboarding_complete is True
        assert user.profile is not None
    finally:
        db.close()
