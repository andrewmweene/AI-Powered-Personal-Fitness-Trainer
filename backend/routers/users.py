"""User registration and profile endpoints."""

from __future__ import annotations

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from .. import auth
from ..dependencies import get_db, get_current_user
from ..models import User
from ..schemas import Token, UserCreate, UserResponse, LoginRequest

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


@router.post("/token", response_model=Token)
def login(credentials: LoginRequest, db: Session = Depends(get_db)) -> Token:
    """Authenticate a user and return a JWT access token."""
    user = db.query(User).filter(User.username == credentials.username).first()
    if user is None:
        logger.debug("Login attempt with unknown username: %s", credentials.username)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")
    verified = auth.verify_password(credentials.password, user.hashed_password)
    if not verified:
        logger.debug("Password verification failed for user: %s", credentials.username)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")
    access_token = auth.create_access_token(data={"sub": str(user.id)})
    return Token(access_token=access_token)


@router.post("/login", response_model=Token)
def login_user(credentials: LoginRequest, db: Session = Depends(get_db)) -> Token:
    """Authenticate a user and return a JWT access token (login alias)."""
    user = db.query(User).filter(User.username == credentials.username).first()
    if user is None:
        logger.debug("Login_user attempt with unknown username: %s", credentials.username)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")
    verified = auth.verify_password(credentials.password, user.hashed_password)
    if not verified:
        logger.debug("Login_user password verification failed for user: %s", credentials.username)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")
    access_token = auth.create_access_token(data={"sub": str(user.id)})
    return Token(access_token=access_token)


@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)) -> User:
    """Return the profile for the currently authenticated user."""
    return current_user
