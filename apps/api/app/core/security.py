from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt

from app.core.settings import settings


def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")[:72]
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    password_bytes = password.encode("utf-8")[:72]
    return bcrypt.checkpw(password_bytes, password_hash.encode("utf-8"))


def _encode_token(subject: str, secret: str, expires_delta: timedelta, token_type: str) -> str:
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def create_access_token(subject: str) -> str:
    return _encode_token(subject, settings.jwt_secret_key, timedelta(minutes=30), "access")


def create_refresh_token(subject: str) -> str:
    return _encode_token(subject, settings.jwt_refresh_secret_key, timedelta(days=7), "refresh")


def decode_access_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.jwt_secret_key, algorithms=["HS256"])


def decode_refresh_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.jwt_refresh_secret_key, algorithms=["HS256"])
