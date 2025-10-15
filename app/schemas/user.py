"""
User schemas
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    country: Optional[str] = None
    timezone: Optional[str] = None
    id_number: Optional[str] = None
    date_of_birth: Optional[datetime] = None


class UserCreate(UserBase):
    """User creation schema"""
    password: str


class UserUpdate(BaseModel):
    """User update schema"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    country: Optional[str] = None
    timezone: Optional[str] = None
    profile_picture: Optional[str] = None
    id_number: Optional[str] = None
    date_of_birth: Optional[datetime] = None


class UserResponse(UserBase):
    """User response schema"""
    id: int
    is_active: bool
    is_verified: bool
    is_admin: bool
    two_factor_enabled: bool
    kyc_status: str
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserProfile(UserResponse):
    """Extended user profile schema"""
    pass


# Password Reset Schemas
class PasswordResetRequest(BaseModel):
    """Password reset request schema"""
    email: EmailStr


class PasswordResetVerify(BaseModel):
    """Password reset verification schema"""
    email: EmailStr
    code: str


class PasswordResetUpdate(BaseModel):
    """Password reset update schema"""
    email: EmailStr
    code: str
    new_password: str


# Email Verification Schemas
class EmailVerificationRequest(BaseModel):
    """Email verification request schema"""
    email: EmailStr


class EmailVerificationVerify(BaseModel):
    """Email verification schema"""
    email: EmailStr
    code: str

