"""Cookie-based refresh-token authentication endpoints."""

from __future__ import annotations

import os

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

from .. import auth
from ..dependencies import get_db
from ..models import User
from ..schemas import LoginRequest, Token

router = APIRouter()
limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])
COOKIE_PATH = "/auth"


def _set_refresh_cookie(response: Response, raw_token: str) -> None:
    response.set_cookie(
        key="refresh_token",
        value=raw_token,
        httponly=True,
        secure=os.getenv("ENV", "development").lower() == "production",
        samesite="strict",
        max_age=auth.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path=COOKIE_PATH,
    )


def _authenticate(credentials: LoginRequest, db: Session) -> User:
    user = db.query(User).filter(User.username == credentials.username).first()
    if user is None or not auth.verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")
    return user


@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
def login(request: Request, response: Response, credentials: LoginRequest, db: Session = Depends(get_db)) -> Token:
    user = _authenticate(credentials, db)
    access_token = auth.create_access_token({"sub": str(user.id)})
    refresh_token = auth.create_refresh_token(str(user.id), db)
    _set_refresh_cookie(response, refresh_token)
    return Token(access_token=access_token)


@router.post("/refresh", response_model=Token)
@limiter.limit("5/minute")
def refresh(request: Request, response: Response, db: Session = Depends(get_db)) -> Token:
    raw_token = request.cookies.get("refresh_token")
    record = auth.verify_refresh_token(raw_token, db) if raw_token else None
    if record is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token.")

    record.revoked = True
    db.commit()
    new_refresh_token = auth.create_refresh_token(record.user_id, db)
    _set_refresh_cookie(response, new_refresh_token)
    return Token(access_token=auth.create_access_token({"sub": str(record.user_id)}))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request, response: Response, db: Session = Depends(get_db)) -> Response:
    raw_token = request.cookies.get("refresh_token")
    if raw_token:
        auth.revoke_refresh_token(raw_token, db)
    response.delete_cookie("refresh_token", path=COOKIE_PATH)
    response.status_code = status.HTTP_204_NO_CONTENT
    return response
