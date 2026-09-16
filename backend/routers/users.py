"""User registration and profile endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session
import logging

from .. import auth
from ..dependencies import get_db, get_current_user
from ..models import User
from ..schemas import UserCreate, UserResponse, LoginRequest
from .auth import _authenticate, _set_refresh_cookie, limiter

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/register", response_model=UserResponse)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)) -> User:
    """Register a new user and return the created profile."""
    existing = db.query(User).filter((User.username == user_in.username) | (User.email == user_in.email)).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists.")
    hashed_password = auth.hash_password(user_in.password)
    user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hashed_password,
        age=user_in.age,
        fitness_level=user_in.fitness_level,
        goal=user_in.goal,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/token")
@router.post("/login")
@limiter.limit("5/minute")
def legacy_login(request: Request, response: Response, credentials: LoginRequest, db: Session = Depends(get_db)) -> dict[str, str]:
    """Compatibility login aliases using the same secure cookie flow."""
    user = _authenticate(credentials, db)
    access_token = auth.create_access_token(data={"sub": str(user.id)})
    _set_refresh_cookie(response, auth.create_refresh_token(str(user.id), db))
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)) -> User:
    """Return the profile for the currently authenticated user."""
    return current_user
