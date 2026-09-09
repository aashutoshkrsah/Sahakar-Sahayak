from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from backend.models.database import get_db
from backend.models.user import User
from backend.models.auth_schemas import (
    UserRegisterRequest,
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
)

router = APIRouter()


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(request: UserRegisterRequest, db: Session = Depends(get_db)):
    """
    Registers a new user with name, unique email, unique phone number, and password.
    Returns the created user details and a signed JWT access token.
    """
    clean_email = request.email.strip().lower()
    clean_phone = normalize_phone(request.phone.strip())

    # 1. Check for duplicate email
    existing_email_user = db.query(User).filter(
        func.lower(User.email) == clean_email
    ).first()
    if existing_email_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered. Please log in or use a different email.",
        )

    # 2. Check for duplicate phone number
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

    # 3. Hash password securely
    hashed_pwd = hash_password(request.password)

    # 4. Create new user entity
    new_user = User(
        name=request.name.strip(),
        email=clean_email,
        phone=clean_phone,
        password_hash=hashed_pwd,
        user_type=request.userType or "Citizen",
        preferred_language=request.preferredLanguage or "en",
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 5. Generate JWT token
    token = create_access_token(
        data={"sub": str(new_user.id), "email": new_user.email, "phone": new_user.phone}
    )

    return AuthResponse(
        success=True,
        token=token,
        user=UserResponse(**new_user.to_dict()),
        message="Registration successful! Welcome to Sahakar Sahayak.",
    )


@router.post("/login", response_model=AuthResponse)
def login(request: UserLoginRequest, db: Session = Depends(get_db)):
    """
    Authenticates a user using EITHER their registered email OR their registered phone number,
    along with their password.
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

    # If not found by email, try matching by phone number
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

    # 4. Issue access token
    token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "phone": user.phone}
    )

    return AuthResponse(
        success=True,
        token=token,
        user=UserResponse(**user.to_dict()),
        message="Login successful! Welcome back.",
    )


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
    Updates the authenticated user's profile details (name, email, phone, userType, preferredLanguage)
    while strictly enforcing email and phone uniqueness against other accounts.
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

    # Re-issue updated token
    token = create_access_token(
        data={"sub": str(current_user.id), "email": current_user.email, "phone": current_user.phone}
    )

    return AuthResponse(
        success=True,
        token=token,
        user=UserResponse(**current_user.to_dict()),
        message="Profile updated successfully.",
    )
