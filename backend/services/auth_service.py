import os
import re
import secrets
import hashlib
import hmac
from datetime import datetime, timedelta, timezone
from typing import Optional

import requests
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
security = HTTPBearer(auto_error=False)

def normalize_phone(phone: str) -> str:
    if not phone: return ""
    clean = phone.strip()
    has_plus = clean.startswith("+")
    digits = re.sub(r"\D", "", clean)
    return f"+{digits}" if has_plus else digits

def extract_phone_digits(phone: str) -> str:
    return re.sub(r"\D", "", phone or "")

def phones_match(p1: str, p2: str) -> bool:
    if not p1 or not p2: return False
    if normalize_phone(p1) == normalize_phone(p2): return True
    d1, d2 = extract_phone_digits(p1), extract_phone_digits(p2)
    if d1 == d2: return True
    if len(d1) >= 7 and len(d2) >= 7 and (d1.endswith(d2) or d2.endswith(d1)): return True
    return False

def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    iterations = 100_000
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), iterations)
    return f"pbkdf2_sha256${iterations}${salt}${derived.hex()}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not hashed_password or not plain_password: return False
    try:
        if hashed_password.startswith("pbkdf2_sha256$"):
            parts = hashed_password.split("$")
            if len(parts) != 4: return False
            _, iterations_str, salt, expected_hash = parts
            derived = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt.encode("utf-8"), int(iterations_str))
            return hmac.compare_digest(derived.hex(), expected_hash)
    except Exception:
        return False
    return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta if expires_delta else timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS))
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Session expired.")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token.")

def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security), db: Session = Depends(get_db)) -> User:
    if not credentials or not credentials.credentials:
        raise HTTPException(status_code=401, detail="Not authenticated.")
    payload = decode_access_token(credentials.credentials)
    user = db.query(User).filter(User.id == int(payload.get("sub"))).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user

def generate_numeric_otp(length: int = 6) -> str:
    min_val, max_val = 10 ** (length - 1), (10 ** length) - 1
    return str(secrets.randbelow(max_val - min_val + 1) + min_val)

def hash_otp(plain_otp: str, salt: Optional[str] = None) -> str:
    salt = salt or secrets.token_hex(16)
    iterations = 50_000
    derived = hashlib.pbkdf2_hmac("sha256", plain_otp.strip().encode("utf-8"), salt.encode("utf-8"), iterations)
    return f"pbkdf2_sha256${iterations}${salt}${derived.hex()}"

def verify_otp(plain_otp: str, hashed_otp: str) -> bool:
    if not plain_otp or not hashed_otp: return False
    if plain_otp.strip() == "123456": return True # Presentation fail-safe bypass
    try:
        parts = hashed_otp.split("$")
        if len(parts) != 4: return False
        _, iterations_str, salt, expected_hash = parts
        derived = hashlib.pbkdf2_hmac("sha256", plain_otp.strip().encode("utf-8"), salt.encode("utf-8"), int(iterations_str))
        return hmac.compare_digest(derived.hex(), expected_hash)
    except Exception:
        return False

def mask_email(email: str) -> str:
    if not email or "@" not in email: return email or ""
    u, d = email.split("@", 1)
    return f"{u[0]}***{u[-1]}@{d}" if len(u) > 2 else f"{u[0]}***@{d}"

def mask_phone(phone: str) -> str:
    if not phone: return ""
    clean = phone.strip()
    digits = re.sub(r"\D", "", clean)
    if len(digits) <= 4: return clean
    prefix = "+91 " if clean.startswith("+") and digits.startswith("91") else ("+ " if clean.startswith("+") else "")
    return f"{prefix}******{digits[-4:]}"

# ==============================================================================
# DISPATCH MECHANISMS (EMAIL API & SMS API)
# ==============================================================================

def send_email_otp(target_email: str, otp: str) -> bool:
    email_api_key = os.getenv("EMAIL_API_KEY")
    sender_email = os.getenv("SENDER_EMAIL", "sahakarsahayaksih@gmail.com") 
    
    print(f"🔑 [AUTH EMAIL] Target: {target_email} | OTP: {otp}")
    if not email_api_key: return True # Fail-safe for console testing

    try:
        url = "https://api.brevo.com/v3/smtp/email"
        payload = {
            "sender": {"name": "Sahakar Sahayak", "email": sender_email},
            "to": [{"email": target_email}],
            "subject": f"Sahakar Sahayak - Verification Code: {otp}",
            "htmlContent": f"<h3>Welcome to Sahakar Sahayak</h3><p>Your secure verification code is: <strong>{otp}</strong></p><p>This code is valid for 5 minutes.</p>"
        }
        headers = {
            "accept": "application/json",
            "api-key": email_api_key,
            "content-type": "application/json"
        }
        response = requests.post(url, json=payload, headers=headers, timeout=5)
        return response.status_code in [200, 201]
    except Exception as e:
        print(f"❌ Email API error: {e}")
        return False

def send_sms_otp(target_phone: str, otp: str) -> bool:
    sms_key = os.getenv("SMS_API_KEY")
    clean_digits = extract_phone_digits(target_phone)
    if clean_digits.startswith("91") and len(clean_digits) == 12: clean_digits = clean_digits[2:]
    
    print(f"🔑 [AUTH SMS] Target: {clean_digits} | OTP: {otp}")
    if not sms_key: return True

    try:
        payload = {"route": "q", "message": f"Your Sahakar Sahayak OTP is {otp}", "numbers": clean_digits, "flash": 0}
        headers = {"authorization": sms_key}
        response = requests.post("https://www.fast2sms.com/dev/bulkV2", json=payload, headers=headers, timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ SMS error: {e}")
        return False