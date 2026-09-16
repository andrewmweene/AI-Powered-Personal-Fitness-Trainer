"""Authentication utilities for hashing passwords and JWT token handling."""

from __future__ import annotations

import os
import hashlib
import secrets
from datetime import datetime, timedelta

import bcrypt
from dotenv import load_dotenv
from jose import JWTError, jwt

from .models import RefreshToken

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

ENVIRONMENT = os.getenv("ENV", "development").lower()
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    if ENVIRONMENT == "production":
        raise RuntimeError("SECRET_KEY must be set when ENV=production")
    SECRET_KEY = "local-development-secret-change-me"
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))


def hash_password(plain: str) -> str:
    """Hash a plain text password using bcrypt.

    Args:
        plain: The plaintext password.

    Returns:
        The bcrypt hashed password as a string.
    """
    hashed = bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plaintext password against a hashed password.

    Args:
        plain: The plaintext password.
        hashed: The stored bcrypt hash.

    Returns:
        True if the password matches the hash, otherwise False.
    """
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        return False


def create_access_token(data: dict[str, str], expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token with an optional expiration.

    Args:
        data: The data payload to encode into the token.
        expires_delta: Optional token lifetime. Defaults to configured minutes.

    Returns:
        A signed JWT string.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


def decode_access_token(token: str) -> dict[str, str] | None:
    """Decode and validate a JWT access token.

    Args:
        token: The JWT token string.

    Returns:
        The decoded payload dictionary, or None if verification fails.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def _hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_refresh_token(user_id: str, db) -> str:
    """Create and persist a hashed opaque refresh token."""
    raw_token = secrets.token_urlsafe(32)
    db.add(
        RefreshToken(
            user_id=user_id,
            token_hash=_hash_refresh_token(raw_token),
            expires_at=datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        )
    )
    db.commit()
    return raw_token


def verify_refresh_token(token: str, db) -> RefreshToken | None:
    """Return an active refresh token record for a raw cookie token."""
    record = db.query(RefreshToken).filter(RefreshToken.token_hash == _hash_refresh_token(token)).first()
    if record is None or record.revoked or record.expires_at <= datetime.utcnow():
        return None
    return record


def revoke_refresh_token(token: str, db) -> None:
    """Revoke a refresh token if it exists."""
    record = db.query(RefreshToken).filter(RefreshToken.token_hash == _hash_refresh_token(token)).first()
    if record is not None:
        record.revoked = True
        db.commit()
