"""
Authentication schemas
"""
from pydantic import BaseModel, EmailStr
from typing import Optional


class UserRegister(BaseModel):
    """User registration schema"""
    email: EmailStr
    username: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    country: Optional[str] = None
    id_number: Optional[str] = None
    date_of_birth: Optional[str] = None  # Will be converted to datetime


class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data"""
    user_id: int


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema"""
    refresh_token: str


class PasswordChange(BaseModel):
    """Password change schema"""
    old_password: str
    new_password: str

