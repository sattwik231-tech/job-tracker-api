from datetime import datetime, timedelta, timezone

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import (
    InvalidHashError,
    VerificationError,
    VerifyMismatchError
)

from app.core.config import settings

#Argon2 password hashing
password_hasher = PasswordHasher()

def hash_password(password: str) -> str:
    """Hash a plain-text password."""
    return password_hasher.hash(password)


def verify_password(
        plain_password: str,
        hashed_password: str,
) -> bool:
    """Check wheather a passowrd matches its stroed hash."""
    try:
        return password_hasher.verify(
            hashed_password,
            plain_password,
        )
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


#JWT access token
def create_access_token(user_id : int) -> str:
    """Create a signed JWT for a user."""
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )

    payload = {
        "sub" : str(user_id),
        "exp" : expires_at, 
    }

    return jwt.encode(
        payload,
        settings.secret_key,
        algorithm=settings.algorithm
    )

def decode_access_token(token : str) -> dict:
    """Decode and validate a JWT"""
    return jwt.decode(
        token,
        settings.secret_key,
        algorithms=[settings.algorithm]
    )