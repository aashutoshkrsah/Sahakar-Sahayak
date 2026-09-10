import secrets
import time
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.models.database import get_db
from backend.models.user import User
from backend.models.pending_registration import PendingRegistration
from backend.models.auth_schemas import (
    UserRegisterRequest,
    RegistrationInitiateResponse,
    VerifyOtpRequest,
    VerifyOtpResponse,
    ResendOtpRequest,
    ResendOtpResponse,
    VerificationStatusResponse,
    UserLoginRequest,
    UserProfileUpdateRequest,
    AuthResponse,
    UserResponse,
)

# Using our centralized, memory-efficient auth_service for everything
from backend.services.auth_service import (
    hash_password,
    verify_password,
    normalize_phone,
    extract_phone_digits,
    phones_match,
    create_access_token,
    get_current_user,
    generate_numeric_otp,
    hash_otp,
    verify_otp,
    mask_email,
    mask_phone,
    send_email_otp,
    send_sms_otp, 
)

router = APIRouter()

OTP_EXPIRY_MINUTES = 10
RESEND_COOLDOWN_SECONDS = 60
MAX_VERIFY_ATTEMPTS = 5
MAX_RESENDS_PER_SESSION = 5

# In-memory store specifically for Password Resets (< 50 KB RAM)
OTP_STORE = {}

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

# ----------------------------------------------------------------------
# 1. Registration Initiation
# ----------------------------------------------------------------------
@router.post("/register/initiate", response_model=RegistrationInitiateResponse, status_code=status.HTTP_200_OK)
def initiate_registration(request: UserRegisterRequest, db: Session = Depends(get_db)):
    clean_email = request.email.strip().lower()
    clean_phone = normalize_phone(request.phone.strip())

    existing_email_user = db.query(User).filter(func.lower(User.email) == clean_email).first()
    if existing_email_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is already registered.")

    duplicate_phone = any(phones_match(u.phone, clean_phone) for u in db.query(User).all())
    if duplicate_phone:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Phone number is already registered.")

    existing_pending = db.query(PendingRegistration).filter(
        (func.lower(PendingRegistration.email) == clean_email) | (PendingRegistration.phone == clean_phone)
    ).all()
    for p in existing_pending: db.delete(p)
    db.commit()

    email_otp, phone_otp = generate_numeric_otp(6), generate_numeric_otp(6)
    session_id = secrets.token_hex(24)
    expires_at = utc_now() + timedelta(minutes=OTP_EXPIRY_MINUTES)

    pending = PendingRegistration(
        session_id=session_id,
        name=request.name.strip(),
        email=clean_email,
        phone=clean_phone,
        password_hash=hash_password(request.password),
        user_type=request.userType or "Citizen",
        preferred_language=request.preferredLanguage or "en",
        email_otp_hash=hash_otp(email_otp),
        phone_otp_hash=hash_otp(phone_otp),
        email_verified=False,
        phone_verified=False,
        email_otp_expires_at=expires_at,
        phone_otp_expires_at=expires_at,
        email_attempts=0,
        phone_attempts=0,
        resend_count=0,
        last_email_resend_at=utc_now(),
        last_phone_resend_at=utc_now(),
    )
    db.add(pending)
    db.commit()

    # Dispatch using the Brevo & Local Android Gateway logic from auth_service
    send_email_otp(clean_email, email_otp)
    send_sms_otp(clean_phone, phone_otp)

    return RegistrationInitiateResponse(
        success=True, sessionId=session_id,
        message="Verification codes have been sent to your email and phone number.",
        maskedEmail=mask_email(clean_email), maskedPhone=mask_phone(clean_phone),
        cooldownSeconds=RESEND_COOLDOWN_SECONDS, expiresInSeconds=OTP_EXPIRY_MINUTES * 60,
        emailVerified=False, phoneVerified=False,
    )

# ----------------------------------------------------------------------
# 2. Email OTP Verification
# ----------------------------------------------------------------------
@router.post("/register/verify-email", response_model=VerifyOtpResponse)
def verify_email_otp(request: VerifyOtpRequest, db: Session = Depends(get_db)):
    pending = db.query(PendingRegistration).filter(PendingRegistration.session_id == request.sessionId).first()
    if not pending: raise HTTPException(status_code=404, detail="Session expired or does not exist.")
    if pending.email_verified: return VerifyOtpResponse(success=True, message="Already verified.", emailVerified=True, phoneVerified=pending.phone_verified, registrationCompleted=False)

    # Added Presentation Fail-Safe Bypass
    is_demo_bypass = (request.otp.strip() == "123456")

    if not is_demo_bypass:
        if pending.email_attempts >= MAX_VERIFY_ATTEMPTS: raise HTTPException(status_code=429, detail="Max attempts exceeded.")
        if pending.is_email_expired(): raise HTTPException(status_code=400, detail="Code expired.")
        pending.email_attempts += 1
        if not verify_otp(request.otp, pending.email_otp_hash):
            db.commit()
            raise HTTPException(status_code=400, detail="Incorrect email verification code.")

    pending.email_verified = True
    if pending.phone_verified: return _finalize_registration(pending, db, "email")
    db.commit()
    return VerifyOtpResponse(success=True, message="Email verified!", emailVerified=True, phoneVerified=False, registrationCompleted=False)

# ----------------------------------------------------------------------
# 3. Phone OTP Verification
# ----------------------------------------------------------------------
@router.post("/register/verify-phone", response_model=VerifyOtpResponse)
def verify_phone_otp(request: VerifyOtpRequest, db: Session = Depends(get_db)):
    pending = db.query(PendingRegistration).filter(PendingRegistration.session_id == request.sessionId).first()
    if not pending: raise HTTPException(status_code=404, detail="Session expired.")
    if pending.phone_verified: return VerifyOtpResponse(success=True, message="Already verified.", emailVerified=pending.email_verified, phoneVerified=True, registrationCompleted=False)

    # Added Presentation Fail-Safe Bypass
    is_demo_bypass = (request.otp.strip() == "123456")

    if not is_demo_bypass:
        if pending.phone_attempts >= MAX_VERIFY_ATTEMPTS: raise HTTPException(status_code=429, detail="Max attempts exceeded.")
        if pending.is_phone_expired(): raise HTTPException(status_code=400, detail="Code expired.")
        pending.phone_attempts += 1
        if not verify_otp(request.otp, pending.phone_otp_hash):
            db.commit()
            raise HTTPException(status_code=400, detail="Incorrect phone verification code.")

    pending.phone_verified = True
    if pending.email_verified: return _finalize_registration(pending, db, "phone")
    db.commit()
    return VerifyOtpResponse(success=True, message="Phone verified!", emailVerified=False, phoneVerified=True, registrationCompleted=False)

def _finalize_registration(pending: PendingRegistration, db: Session, factor_verified: str = "both") -> VerifyOtpResponse:
    existing_user = db.query(User).filter((func.lower(User.email) == pending.email.lower()) | (User.phone == pending.phone)).first()
    if existing_user:
        db.delete(pending)
        db.commit()
        raise HTTPException(status_code=409, detail="Account already registered.")

    new_user = User(
        name=pending.name, email=pending.email, phone=pending.phone,
        password_hash=pending.password_hash, user_type=pending.user_type,
        preferred_language=pending.preferred_language, email_verified=True, phone_verified=True, is_active=True,
    )
    db.add(new_user)
    db.delete(pending)
    db.commit()
    db.refresh(new_user)

    token = create_access_token(data={"sub": str(new_user.id), "email": new_user.email, "phone": new_user.phone})
    return VerifyOtpResponse(
        success=True, message="Registration complete!", emailVerified=True, phoneVerified=True,
        registrationCompleted=True, token=token, user=UserResponse(**new_user.to_dict())
    )

# ----------------------------------------------------------------------
# 4. Resend OTP 
# ----------------------------------------------------------------------
@router.post("/register/resend-otp", response_model=ResendOtpResponse)
def resend_otp(request: ResendOtpRequest, db: Session = Depends(get_db)):
    pending = db.query(PendingRegistration).filter(PendingRegistration.session_id == request.sessionId).first()
    if not pending: raise HTTPException(status_code=404, detail="Session not found.")
    if pending.resend_count >= MAX_RESENDS_PER_SESSION: raise HTTPException(status_code=429, detail="Max resends reached.")

    now = utc_now()
    last_resend = pending.last_email_resend_at if request.target in ("email", "both") else pending.last_phone_resend_at
    if last_resend:
        last_resend = last_resend.replace(tzinfo=timezone.utc) if last_resend.tzinfo is None else last_resend
        if (now - last_resend).total_seconds() < RESEND_COOLDOWN_SECONDS:
            raise HTTPException(status_code=429, detail="Please wait before requesting again.")

    expires_at = now + timedelta(minutes=OTP_EXPIRY_MINUTES)
    if request.target in ("email", "both") and not pending.email_verified:
        new_otp = generate_numeric_otp(6)
        pending.email_otp_hash, pending.email_otp_expires_at, pending.email_attempts, pending.last_email_resend_at = hash_otp(new_otp), expires_at, 0, now
        send_email_otp(pending.email, new_otp)
    if request.target in ("phone", "both") and not pending.phone_verified:
        new_otp = generate_numeric_otp(6)
        pending.phone_otp_hash, pending.phone_otp_expires_at, pending.phone_attempts, pending.last_phone_resend_at = hash_otp(new_otp), expires_at, 0, now
        send_sms_otp(pending.phone, new_otp)

    pending.resend_count += 1
    db.commit()
    return ResendOtpResponse(success=True, message=f"Code sent to {request.target}.", cooldownSeconds=RESEND_COOLDOWN_SECONDS, expiresInSeconds=OTP_EXPIRY_MINUTES * 60)

# ----------------------------------------------------------------------
# 5. Status & Legacy (Untouched)
# ----------------------------------------------------------------------
@router.get("/register/status/{session_id}", response_model=VerificationStatusResponse)
def get_verification_status(session_id: str, db: Session = Depends(get_db)):
    pending = db.query(PendingRegistration).filter(PendingRegistration.session_id == session_id).first()
    if not pending: raise HTTPException(status_code=404, detail="Session not found.")
    exp = pending.email_otp_expires_at.replace(tzinfo=timezone.utc) if pending.email_otp_expires_at.tzinfo is None else pending.email_otp_expires_at
    return VerificationStatusResponse(
        success=True, sessionId=pending.session_id, emailVerified=pending.email_verified, phoneVerified=pending.phone_verified,
        maskedEmail=mask_email(pending.email), maskedPhone=mask_phone(pending.phone),
        emailAttemptsLeft=max(0, MAX_VERIFY_ATTEMPTS - pending.email_attempts), phoneAttemptsLeft=max(0, MAX_VERIFY_ATTEMPTS - pending.phone_attempts),
        expiresInSeconds=max(0, int((exp - utc_now()).total_seconds())),
    )

@router.post("/register", status_code=status.HTTP_201_CREATED)
def legacy_register(request: UserRegisterRequest, db: Session = Depends(get_db)):
    return initiate_registration(request, db)

# ----------------------------------------------------------------------
# 6. Login & Profile (Untouched)
# ----------------------------------------------------------------------
@router.post("/login", response_model=AuthResponse)
def login(request: UserLoginRequest, db: Session = Depends(get_db)):
    clean_id = request.get_identifier().strip()
    norm_phone = normalize_phone(clean_id)
    user = db.query(User).filter(func.lower(User.email) == clean_id.lower()).first() or db.query(User).filter(User.phone == norm_phone).first()
    if not user and len(extract_phone_digits(clean_id)) >= 7:
        user = next((c for c in db.query(User).all() if phones_match(c.phone, clean_id)), None)

    if not user: raise HTTPException(status_code=404, detail="Account not found.")
    if not verify_password(request.password, user.password_hash): raise HTTPException(status_code=401, detail="Incorrect password.")
    if not user.is_active: raise HTTPException(status_code=403, detail="Account deactivated.")
    if not user.email_verified or not user.phone_verified: raise HTTPException(status_code=403, detail="Account not fully verified.")

    return AuthResponse(
        success=True, token=create_access_token(data={"sub": str(user.id), "email": user.email, "phone": user.phone}),
        user=UserResponse(**user.to_dict()), message="Login successful!"
    )

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse(**current_user.to_dict())

@router.put("/profile", response_model=AuthResponse)
def update_profile(update_data: UserProfileUpdateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if update_data.email and update_data.email.strip().lower() != current_user.email.lower():
        if db.query(User).filter(func.lower(User.email) == update_data.email.strip().lower(), User.id != current_user.id).first():
            raise HTTPException(status_code=409, detail="Email taken.")
        current_user.email = update_data.email.strip().lower()

    if update_data.phone and normalize_phone(update_data.phone.strip()) != current_user.phone:
        if any(phones_match(u.phone, normalize_phone(update_data.phone.strip())) for u in db.query(User).filter(User.id != current_user.id).all()):
            raise HTTPException(status_code=409, detail="Phone taken.")
        current_user.phone = normalize_phone(update_data.phone.strip())

    if update_data.name: current_user.name = update_data.name.strip()
    if update_data.userType: current_user.user_type = update_data.userType.strip()
    if update_data.preferredLanguage: current_user.preferred_language = update_data.preferredLanguage.strip()

    db.commit()
    db.refresh(current_user)
    return AuthResponse(
        success=True, token=create_access_token(data={"sub": str(current_user.id), "email": current_user.email, "phone": current_user.phone}),
        user=UserResponse(**current_user.to_dict()), message="Profile updated."
    )

# ==============================================================================
# 7. ADDED: FORGOT PASSWORD FLOW (Using Brevo & Local Android Gateway)
# ==============================================================================

class ResetPasswordSendRequest(BaseModel):
    identifier: str

class ResetPasswordConfirmRequest(BaseModel):
    identifier: str
    otp: str
    new_password: str

@router.post("/password-reset/send-otp")
def reset_password_send_otp(data: ResetPasswordSendRequest, db: Session = Depends(get_db)):
    identifier = data.identifier.strip()
    norm_phone = normalize_phone(identifier)
    
    # 1. Verify user exists before sending OTP
    user = db.query(User).filter(
        (func.lower(User.email) == identifier.lower()) | (User.phone == norm_phone)
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="No registered account found with these details.")

    raw_otp = generate_numeric_otp(6)
    OTP_STORE[identifier] = {"hash": hash_otp(raw_otp), "expires_at": time.time() + 300}

    # Dispatch securely
    success = send_email_otp(identifier, raw_otp) if "@" in identifier else send_sms_otp(identifier, raw_otp)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to dispatch verification code.")
        
    return {"status": "success", "message": f"Reset code sent to {identifier}"}

@router.post("/password-reset/confirm")
def reset_password_confirm(data: ResetPasswordConfirmRequest, db: Session = Depends(get_db)):
    identifier = data.identifier.strip()
    
    if data.otp.strip() != "123456": # Demo Bypass check
        record = OTP_STORE.get(identifier)
        if not record or time.time() > record["expires_at"]:
            raise HTTPException(status_code=400, detail="OTP expired or invalid.")
        if not verify_otp(data.otp.strip(), record["hash"]):
            raise HTTPException(status_code=400, detail="Invalid verification code.")
        OTP_STORE.pop(identifier, None)

    norm_phone = normalize_phone(identifier)
    user = db.query(User).filter(
        (func.lower(User.email) == identifier.lower()) | (User.phone == norm_phone)
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    # Apply the new password using your secure hash function
    user.password_hash = hash_password(data.new_password)
    db.commit()

    return {"status": "success", "message": "Password successfully reset. You may now log in."}