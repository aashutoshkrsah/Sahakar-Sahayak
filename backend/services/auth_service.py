import os
import re
import secrets
import hashlib
import hmac
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from backend.models.database import get_db
from backend.models.user import User

# Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "sahakar-sahayak-production-auth-key-secret-2026")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7

# Security scheme for FastAPI docs / header parsing
security = HTTPBearer(auto_error=False)


def normalize_phone(phone: str) -> str:
    """
    Normalizes a phone number for robust comparison and storage.
    Removes common formatting characters (spaces, dashes, parentheses, dots).
    Preserves leading '+' if present.
    Example: '+91 98765-43210' -> '+919876543210'
    """
    if not phone:
        return ""
    clean = phone.strip()
    has_plus = clean.startswith("+")
    digits = re.sub(r"\D", "", clean)
    return f"+{digits}" if has_plus else digits


def extract_phone_digits(phone: str) -> str:
    """Extract only the numeric digits from a phone number string."""
    return re.sub(r"\D", "", phone or "")


def phones_match(p1: str, p2: str) -> bool:
    """
    Checks if two phone numbers refer to the same phone,
    taking into account country prefixes and formatting.
    """
    if not p1 or not p2:
        return False
    norm1 = normalize_phone(p1)
    norm2 = normalize_phone(p2)
    if norm1 == norm2:
        return True
    d1 = extract_phone_digits(p1)
    d2 = extract_phone_digits(p2)
    if d1 == d2:
        return True
    if len(d1) >= 7 and len(d2) >= 7:
        if d1.endswith(d2) or d2.endswith(d1):
            return True
    return False


def hash_password(password: str) -> str:
    """
    Hashes a password using PBKDF2-HMAC-SHA256 with 100,000 iterations and a 16-byte random salt.
    Guaranteed cross-platform, standard NIST-approved security, zero binary dependency failures.
    Format: pbkdf2_sha256$<iterations>$<salt_hex>$<hash_hex>
    """
    salt = secrets.token_hex(16)
    iterations = 100_000
    derived = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations
    )
    return f"pbkdf2_sha256${iterations}${salt}${derived.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against the stored password hash using constant-time comparison.
    Supports PBKDF2-HMAC-SHA256 and Argon2 if present.
    """
    if not hashed_password or not plain_password:
        return False

    try:
        if hashed_password.startswith("pbkdf2_sha256$"):
            parts = hashed_password.split("$")
            if len(parts) != 4:
                return False
            _, iterations_str, salt, expected_hash = parts
            iterations = int(iterations_str)
            derived = hashlib.pbkdf2_hmac(
                "sha256",
                plain_password.encode("utf-8"),
                salt.encode("utf-8"),
                iterations
            )
            return hmac.compare_digest(derived.hex(), expected_hash)
        
        # Optional fallback if argon2 hash is detected
        if hashed_password.startswith("$argon2"):
            try:
                import argon2
                ph = argon2.PasswordHasher()
                return ph.verify(hashed_password, plain_password)
            except Exception:
                return False

    except Exception:
        return False

    return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generates a signed JWT token containing user identity and expiration."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """Decodes and validates a JWT token."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has expired. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    FastAPI dependency to retrieve the current authenticated User from the Bearer token.
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    payload = decode_access_token(token)
    user_id = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User account no longer exists.",
        )

    return user
