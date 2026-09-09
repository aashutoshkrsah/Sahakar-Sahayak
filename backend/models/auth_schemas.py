from typing import Optional
from pydantic import BaseModel, Field, field_validator
import re


class UserRegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=120, description="Full name of the user")
    email: str = Field(..., description="Valid unique email address")
    phone: str = Field(..., min_length=7, max_length=30, description="Valid unique phone number")
    password: str = Field(..., min_length=6, max_length=128, description="User password")
    userType: Optional[str] = Field("Citizen", description="Role or user category")
    preferredLanguage: Optional[str] = Field("en", description="Preferred language code (en, hi, kn, ne)")

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        clean = v.strip().lower()
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", clean):
            raise ValueError("Please provide a valid email address format.")
        return clean

    @field_validator("phone")
    @classmethod
    def validate_phone_format(cls, v: str) -> str:
        clean = v.strip()
        digits = re.sub(r"\D", "", clean)
        if len(digits) < 7:
            raise ValueError("Phone number must contain at least 7 digits.")
        return clean

    @field_validator("name")
    @classmethod
    def validate_name_not_empty(cls, v: str) -> str:
        clean = v.strip()
        if len(clean) < 2:
            raise ValueError("Name must be at least 2 characters long.")
        return clean


class UserLoginRequest(BaseModel):
    identifier: Optional[str] = Field(None, description="Email or phone number of the registered user")
    email: Optional[str] = Field(None, description="Optional email alias for identifier")
    phone: Optional[str] = Field(None, description="Optional phone alias for identifier")
    password: str = Field(..., min_length=1, description="Password")

    def get_identifier(self) -> str:
        raw = self.identifier or self.email or self.phone or ""
        return raw.strip()


class UserProfileUpdateRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    userType: Optional[str] = None
    preferredLanguage: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    userType: str
    preferredLanguage: str
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None


class AuthResponse(BaseModel):
    success: bool = True
    token: str
    user: UserResponse
    message: Optional[str] = "Authentication successful"
