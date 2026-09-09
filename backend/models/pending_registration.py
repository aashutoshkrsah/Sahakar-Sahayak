from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from backend.models.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class PendingRegistration(Base):
    """
    Temporary table holding unverified user registrations until BOTH email and phone OTPs
    have been successfully verified. Upon full verification, the account is transferred to
    the permanent `users` table and this pending record is safely removed.
    """
    __tablename__ = "pending_registrations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(120), nullable=False)
    email = Column(String(255), index=True, nullable=False)
    phone = Column(String(50), index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    user_type = Column(String(50), default="Citizen", nullable=False)
    preferred_language = Column(String(10), default="en", nullable=False)

    # Verification state
    email_otp_hash = Column(String(255), nullable=False)
    phone_otp_hash = Column(String(255), nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)
    phone_verified = Column(Boolean, default=False, nullable=False)

    # Expirations (5-10 minutes from generation)
    email_otp_expires_at = Column(DateTime, nullable=False)
    phone_otp_expires_at = Column(DateTime, nullable=False)

    # Attempt counts (Max 5 attempts allowed)
    email_attempts = Column(Integer, default=0, nullable=False)
    phone_attempts = Column(Integer, default=0, nullable=False)

    # Rate limiting & resends
    resend_count = Column(Integer, default=0, nullable=False)
    last_email_resend_at = Column(DateTime, nullable=True)
    last_phone_resend_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    def is_email_expired(self) -> bool:
        now = utc_now()
        exp = self.email_otp_expires_at
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)
        return now > exp

    def is_phone_expired(self) -> bool:
        now = utc_now()
        exp = self.phone_otp_expires_at
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)
        return now > exp

    def is_fully_verified(self) -> bool:
        return bool(self.email_verified and self.phone_verified)

    def __repr__(self):
        return f"<PendingRegistration(session_id='{self.session_id}', email='{self.email}', email_v={self.email_verified}, phone_v={self.phone_verified})>"
