"""Authentication utilities for hashing passwords and JWT token handling."""

from __future__ import annotations

import os
from datetime import datetime, timedelta

import bcrypt
from jose import JWTError, jwt

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))


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
