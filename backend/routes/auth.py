import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
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
)
from backend.services.notification_service import (
    send_email_otp,
    send_phone_otp,
)

router = APIRouter()

OTP_EXPIRY_MINUTES = 10
RESEND_COOLDOWN_SECONDS = 60
MAX_VERIFY_ATTEMPTS = 5
MAX_RESENDS_PER_SESSION = 5


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


# ----------------------------------------------------------------------
# 1. Registration Initiation: Validates, generates 2 OTPs, dispatches
# ----------------------------------------------------------------------
@router.post(
    "/register/initiate",
    response_model=RegistrationInitiateResponse,
    status_code=status.HTTP_200_OK,
)
def initiate_registration(
    request: UserRegisterRequest,
    db: Session = Depends(get_db),
):
    """
    Step 1 of Registration:
    - Validates email format and Indian phone number.
    - Checks whether email or phone number is already registered in active accounts.
    - Generates separate cryptographically secure OTPs for Email and Phone.
    - Securely stores salted hashes in pending_registrations.
    - Dispatches Email OTP and SMS OTP.
    - Returns session details WITHOUT exposing OTPs.
    """
    clean_email = request.email.strip().lower()
    clean_phone = normalize_phone(request.phone.strip())

    # 1. Check for duplicate email in permanent users table
    existing_email_user = db.query(User).filter(
        func.lower(User.email) == clean_email
    ).first()
    if existing_email_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered. Please log in or use a different email.",
        )

    # 2. Check for duplicate phone number in permanent users table
    all_users = db.query(User).all()
    duplicate_phone = any(
        phones_match(u.phone, clean_phone)
        for u in all_users
    )
    if duplicate_phone:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Phone number is already registered. Please log in or use a different phone number.",
        )

    # 3. Clean up any previous pending registrations for this email or phone
    existing_pending = db.query(PendingRegistration).filter(
        (func.lower(PendingRegistration.email) == clean_email) |
        (PendingRegistration.phone == clean_phone)
    ).all()
    for p in existing_pending:
        db.delete(p)
    db.commit()

    # 4. Generate secure OTPs and hashes
    email_otp = generate_numeric_otp(6)
    phone_otp = generate_numeric_otp(6)

    email_otp_hash = hash_otp(email_otp)
    phone_otp_hash = hash_otp(phone_otp)

    # 5. Hash user password securely
    hashed_pwd = hash_password(request.password)

    session_id = secrets.token_hex(24)
    expires_at = utc_now() + timedelta(minutes=OTP_EXPIRY_MINUTES)

    # 6. Save temporary pending record (account not activated yet!)
    pending = PendingRegistration(
        session_id=session_id,
        name=request.name.strip(),
        email=clean_email,
        phone=clean_phone,
        password_hash=hashed_pwd,
        user_type=request.userType or "Citizen",
        preferred_language=request.preferredLanguage or "en",
        email_otp_hash=email_otp_hash,
        phone_otp_hash=phone_otp_hash,
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

    # 7. Dispatch notifications
    send_email_otp(clean_email, request.name.strip(), email_otp)
    send_phone_otp(clean_phone, phone_otp)

    return RegistrationInitiateResponse(
        success=True,
        sessionId=session_id,
        message="Verification codes have been sent to your email and phone number.",
        maskedEmail=mask_email(clean_email),
        maskedPhone=mask_phone(clean_phone),
        cooldownSeconds=RESEND_COOLDOWN_SECONDS,
        expiresInSeconds=OTP_EXPIRY_MINUTES * 60,
        emailVerified=False,
        phoneVerified=False,
    )


# ----------------------------------------------------------------------
# 2. Email OTP Verification
# ----------------------------------------------------------------------
@router.post("/register/verify-email", response_model=VerifyOtpResponse)
def verify_email_otp(request: VerifyOtpRequest, db: Session = Depends(get_db)):
    """
    Verifies the email verification OTP code.
    If phone is also already verified, completes registration and activates account.
    """
    pending = db.query(PendingRegistration).filter(
        PendingRegistration.session_id == request.sessionId
    ).first()

    if not pending:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Verification session has expired or does not exist. Please register again.",
        )

    # If email already verified, return current state
    if pending.email_verified:
        return VerifyOtpResponse(
            success=True,
            message="Email is already verified.",
            emailVerified=True,
            phoneVerified=pending.phone_verified,
            registrationCompleted=False,
        )

    # Check attempt limit
    if pending.email_attempts >= MAX_VERIFY_ATTEMPTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Maximum email verification attempts exceeded. Please request a new OTP code.",
        )

    # Check expiration
    if pending.is_email_expired():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email verification code has expired. Please request a new code.",
        )

    # Increment attempt count
    pending.email_attempts += 1

    # Verify salted hash
    if not verify_otp(request.otp, pending.email_otp_hash):
        db.commit()
        remaining = max(0, MAX_VERIFY_ATTEMPTS - pending.email_attempts)
        if remaining == 0:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Incorrect verification code. Maximum attempts reached. Please request a new OTP code.",
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Incorrect email verification code. {remaining} attempt(s) remaining.",
        )

    # OTP is valid! Mark email as verified
    pending.email_verified = True

    # Check if BOTH factors are now verified
    if pending.phone_verified:
        # Finalize and activate the user account in permanent table
        return _finalize_registration(pending, db, factor_verified="email")

    db.commit()
    return VerifyOtpResponse(
        success=True,
        message="Email verified successfully! Please verify your phone number to complete registration.",
        emailVerified=True,
        phoneVerified=False,
        registrationCompleted=False,
    )


# ----------------------------------------------------------------------
# 3. Phone OTP Verification
# ----------------------------------------------------------------------
@router.post("/register/verify-phone", response_model=VerifyOtpResponse)
def verify_phone_otp(request: VerifyOtpRequest, db: Session = Depends(get_db)):
    """
    Verifies the phone verification OTP code.
    If email is also already verified, completes registration and activates account.
    """
    pending = db.query(PendingRegistration).filter(
        PendingRegistration.session_id == request.sessionId
    ).first()

    if not pending:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Verification session has expired or does not exist. Please register again.",
        )

    # If phone already verified, return current state
    if pending.phone_verified:
        return VerifyOtpResponse(
            success=True,
            message="Phone number is already verified.",
            emailVerified=pending.email_verified,
            phoneVerified=True,
            registrationCompleted=False,
        )

    # Check attempt limit
    if pending.phone_attempts >= MAX_VERIFY_ATTEMPTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Maximum phone verification attempts exceeded. Please request a new OTP code.",
        )

    # Check expiration
    if pending.is_phone_expired():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone verification code has expired. Please request a new code.",
        )

    # Increment attempt count
    pending.phone_attempts += 1

    # Verify salted hash
    if not verify_otp(request.otp, pending.phone_otp_hash):
        db.commit()
        remaining = max(0, MAX_VERIFY_ATTEMPTS - pending.phone_attempts)
        if remaining == 0:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Incorrect verification code. Maximum attempts reached. Please request a new OTP code.",
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Incorrect phone verification code. {remaining} attempt(s) remaining.",
        )

    # OTP is valid! Mark phone as verified
    pending.phone_verified = True

    # Check if BOTH factors are now verified
    if pending.email_verified:
        # Finalize and activate user account in permanent table
        return _finalize_registration(pending, db, factor_verified="phone")

    db.commit()
    return VerifyOtpResponse(
        success=True,
        message="Phone verified successfully! Please verify your email to complete registration.",
        emailVerified=False,
        phoneVerified=True,
        registrationCompleted=False,
    )


def _finalize_registration(
    pending: PendingRegistration,
    db: Session,
    factor_verified: str = "both",
) -> VerifyOtpResponse:
    """
    Internal helper: Transfers verified registration to the permanent `users` table,
    deletes temporary pending record, and generates authenticated JWT token.
    """
    # Guard against race condition for duplicate email/phone
    existing_user = db.query(User).filter(
        (func.lower(User.email) == pending.email.lower()) |
        (User.phone == pending.phone)
    ).first()

    if existing_user:
        db.delete(pending)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email or phone number is already registered.",
        )

    new_user = User(
        name=pending.name,
        email=pending.email,
        phone=pending.phone,
        password_hash=pending.password_hash,
        user_type=pending.user_type,
        preferred_language=pending.preferred_language,
        email_verified=True,
        phone_verified=True,
        is_active=True,
    )

    db.add(new_user)
    db.delete(pending)
    db.commit()
    db.refresh(new_user)

    token = create_access_token(
        data={"sub": str(new_user.id), "email": new_user.email, "phone": new_user.phone}
    )

    return VerifyOtpResponse(
        success=True,
        message="Both email and phone number verified successfully! Welcome to Sahakar Sahayak.",
        emailVerified=True,
        phoneVerified=True,
        registrationCompleted=True,
        token=token,
        user=UserResponse(**new_user.to_dict()),
    )


# ----------------------------------------------------------------------
# 4. Resend OTP with Cooldown & Abuse Protection
# ----------------------------------------------------------------------
@router.post("/register/resend-otp", response_model=ResendOtpResponse)
def resend_otp(request: ResendOtpRequest, db: Session = Depends(get_db)):
    """
    Resends OTP for email, phone, or both with 60-second cooldown rate-limiting.
    """
    pending = db.query(PendingRegistration).filter(
        PendingRegistration.session_id == request.sessionId
    ).first()

    if not pending:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Verification session not found. Please initiate registration again.",
        )

    # Max resends check per session
    if pending.resend_count >= MAX_RESENDS_PER_SESSION:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Maximum resend limit reached for this registration session. Please start over.",
        )

    now = utc_now()

    # Cooldown check
    last_resend = None
    if request.target in ("email", "both"):
        last_resend = pending.last_email_resend_at
    elif request.target == "phone":
        last_resend = pending.last_phone_resend_at

    if last_resend:
        if last_resend.tzinfo is None:
            last_resend = last_resend.replace(tzinfo=timezone.utc)
        elapsed = (now - last_resend).total_seconds()
        if elapsed < RESEND_COOLDOWN_SECONDS:
            remaining = int(RESEND_COOLDOWN_SECONDS - elapsed)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Please wait {remaining} second(s) before requesting a new code.",
            )

    expires_at = now + timedelta(minutes=OTP_EXPIRY_MINUTES)
    dispatched_targets = []

    if request.target in ("email", "both") and not pending.email_verified:
        new_email_otp = generate_numeric_otp(6)
        pending.email_otp_hash = hash_otp(new_email_otp)
        pending.email_otp_expires_at = expires_at
        pending.email_attempts = 0
        pending.last_email_resend_at = now
        send_email_otp(pending.email, pending.name, new_email_otp)
        dispatched_targets.append("email")

    if request.target in ("phone", "both") and not pending.phone_verified:
        new_phone_otp = generate_numeric_otp(6)
        pending.phone_otp_hash = hash_otp(new_phone_otp)
        pending.phone_otp_expires_at = expires_at
        pending.phone_attempts = 0
        pending.last_phone_resend_at = now
        send_phone_otp(pending.phone, new_phone_otp)
        dispatched_targets.append("phone")

    pending.resend_count += 1
    db.commit()

    target_str = " and ".join(dispatched_targets) or request.target
    return ResendOtpResponse(
        success=True,
        message=f"A fresh verification code has been sent to your {target_str}.",
        cooldownSeconds=RESEND_COOLDOWN_SECONDS,
        expiresInSeconds=OTP_EXPIRY_MINUTES * 60,
    )


# ----------------------------------------------------------------------
# 5. Verification Status Check
# ----------------------------------------------------------------------
@router.get("/register/status/{session_id}", response_model=VerificationStatusResponse)
def get_verification_status(session_id: str, db: Session = Depends(get_db)):
    """
    Returns current verification status, remaining attempts, and time left.
    """
    pending = db.query(PendingRegistration).filter(
        PendingRegistration.session_id == session_id
    ).first()

    if not pending:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Verification session not found or has expired.",
        )

    now = utc_now()
    exp = pending.email_otp_expires_at
    if exp.tzinfo is None:
        exp = exp.replace(tzinfo=timezone.utc)
    remaining_secs = max(0, int((exp - now).total_seconds()))

    return VerificationStatusResponse(
        success=True,
        sessionId=pending.session_id,
        emailVerified=pending.email_verified,
        phoneVerified=pending.phone_verified,
        maskedEmail=mask_email(pending.email),
        maskedPhone=mask_phone(pending.phone),
        emailAttemptsLeft=max(0, MAX_VERIFY_ATTEMPTS - pending.email_attempts),
        phoneAttemptsLeft=max(0, MAX_VERIFY_ATTEMPTS - pending.phone_attempts),
        expiresInSeconds=remaining_secs,
    )


# ----------------------------------------------------------------------
# 6. Legacy / Direct Register Endpoint Compatibility
# ----------------------------------------------------------------------
@router.post("/register", status_code=status.HTTP_201_CREATED)
def legacy_register(
    request: UserRegisterRequest,
    db: Session = Depends(get_db),
):
    """
    Direct registration endpoint.
    Initiates registration and returns the verification session token, requiring dual OTP verification.
    """
    init_res = initiate_registration(request, db)
    return init_res


# ----------------------------------------------------------------------
# 7. Dual Identifier Login: Email OR Phone + Password
# ----------------------------------------------------------------------
@router.post("/login", response_model=AuthResponse)
def login(request: UserLoginRequest, db: Session = Depends(get_db)):
    """
    Authenticates an active user using EITHER their registered email OR their registered phone number,
    along with their password. Enforces verification check.
    """
    identifier = request.get_identifier()
    if not identifier:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide your registered email or phone number.",
        )

    if not request.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide your password.",
        )

    clean_id = identifier.strip()
    norm_phone = normalize_phone(clean_id)
    id_digits = extract_phone_digits(clean_id)

    # 1. Search for user by email OR phone number
    user = db.query(User).filter(func.lower(User.email) == clean_id.lower()).first()

    # If not found by email, try matching by normalized phone
    if not user:
        user = db.query(User).filter(User.phone == norm_phone).first()

    # If still not found and digits are at least 7, compare with phones_match
    if not user and len(id_digits) >= 7:
        for candidate in db.query(User).all():
            if phones_match(candidate.phone, clean_id):
                user = candidate
                break

    # 2. Reject unregistered email/phone with clear error
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No account found with this email or phone number. Please register first.",
        )

    # 3. Reject incorrect password with clear error
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password. Please check your password and try again.",
        )

    # 4. Verify account active & verification status
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated. Please contact support.",
        )

    if not user.email_verified or not user.phone_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is not fully verified. Please complete email and phone verification.",
        )

    # 5. Issue access token
    token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "phone": user.phone}
    )

    return AuthResponse(
        success=True,
        token=token,
        user=UserResponse(**user.to_dict()),
        message="Login successful! Welcome back to Sahakar Sahayak.",
    )


# ----------------------------------------------------------------------
# 8. User Profile Endpoints
# ----------------------------------------------------------------------
@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Returns the authenticated user's profile details."""
    return UserResponse(**current_user.to_dict())


@router.put("/profile", response_model=AuthResponse)
def update_profile(
    update_data: UserProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Updates the authenticated user's profile details while enforcing email and phone uniqueness.
    """
    # Check email uniqueness if email is changed
    if update_data.email and update_data.email.strip().lower() != current_user.email.lower():
        new_email = update_data.email.strip().lower()
        conflict = db.query(User).filter(
            func.lower(User.email) == new_email,
            User.id != current_user.id
        ).first()
        if conflict:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This email address is already taken by another account.",
            )
        current_user.email = new_email

    # Check phone uniqueness if phone is changed
    if update_data.phone and normalize_phone(update_data.phone.strip()) != current_user.phone:
        new_phone = normalize_phone(update_data.phone.strip())
        other_users = db.query(User).filter(User.id != current_user.id).all()
        conflict = any(
            phones_match(u.phone, new_phone)
            for u in other_users
        )
        if conflict:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This phone number is already taken by another account.",
            )
        current_user.phone = new_phone

    if update_data.name:
        current_user.name = update_data.name.strip()
    if update_data.userType:
        current_user.user_type = update_data.userType.strip()
    if update_data.preferredLanguage:
        current_user.preferred_language = update_data.preferredLanguage.strip()

    db.commit()
    db.refresh(current_user)

    token = create_access_token(
        data={"sub": str(current_user.id), "email": current_user.email, "phone": current_user.phone}
    )

    return AuthResponse(
        success=True,
        token=token,
        user=UserResponse(**current_user.to_dict()),
        message="Profile updated successfully.",
    )
