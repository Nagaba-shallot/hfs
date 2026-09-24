import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any

import bcrypt
import jwt

from hospital_feedback_system.config import settings


def hash_password(password: str) -> str:
    return bcrypt.hashpw(
        password.encode("utf-8"), bcrypt.gensalt(rounds=settings.BCRYPT_ROUNDS)
    ).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        return False


@lru_cache(maxsize=1)
def _dummy_hash() -> str:
    return hash_password(secrets.token_urlsafe(16))


def burn_password_check(plain: str) -> None:
    verify_password(plain, _dummy_hash())



def _load_key(inline: str | None, path: str, label: str) -> str:
    if inline:
        return inline.replace("\\n", "\n")
    key_path = Path(path)
    if not key_path.is_file():
        raise RuntimeError(
            f"{label} is not configured. Set {label} to the PEM text, or create {path}:\n"
            "  openssl genrsa -out keys/private.pem 2048\n"
            "  openssl rsa -in keys/private.pem -pubout -out keys/public.pem"
        )
    return key_path.read_text()


@lru_cache(maxsize=1)
def get_private_key() -> str:
    return _load_key(settings.PRIVATE_KEY, settings.PRIVATE_KEY_PATH, "PRIVATE_KEY")


@lru_cache(maxsize=1)
def get_public_key() -> str:
    return _load_key(settings.PUBLIC_KEY, settings.PUBLIC_KEY_PATH, "PUBLIC_KEY")


_REQUIRED_CLAIMS = ["exp", "iat", "sub"]
_CLOCK_SKEW_SECONDS = 10


def create_access_token(subject: str | int, extra: dict[str, Any] | None = None) -> str:
    now = datetime.now(timezone.utc)
    claims: dict[str, Any] = dict(extra or {})
    claims.update(
        {
            "sub": str(subject),
            "iat": now,
            "exp": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        }
    )
    return jwt.encode(claims, get_private_key(), algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    return jwt.decode(
        token,
        get_public_key(),
        algorithms=[settings.ALGORITHM],
        options={"require": _REQUIRED_CLAIMS},
        leeway=_CLOCK_SKEW_SECONDS,
    )


def generate_session_token() -> str:
    return secrets.token_urlsafe(32)


def hash_session_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def generate_qr_token() -> str:
    return secrets.token_urlsafe(16)