"""Tests for authentication utility functions."""

from backend.auth import create_access_token, decode_access_token, hash_password, verify_password


def test_password_hashing_and_verification() -> None:
    password = "secret123"
    hashed = hash_password(password)
    assert verify_password(password, hashed)
    assert not verify_password("wrongpass", hashed)


def test_jwt_token_encode_decode() -> None:
    token = create_access_token({"sub": "1"})
    payload = decode_access_token(token)
    assert payload is not None
    assert payload.get("sub") == "1"
