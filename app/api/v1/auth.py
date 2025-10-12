"""
Authentication endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
)
from app.schemas.auth import UserRegister, UserLogin, Token, RefreshTokenRequest
from app.schemas.user import UserResponse, UserCreate
from app.crud import user as user_crud
from app.crud import audit_log as audit_crud
from app.services.email_service import email_service
from app.core.config import settings
from app.models.user import User

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user"""
    
    # Check if user already exists
    existing_user = await user_crud.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    existing_username = await user_crud.get_user_by_username(db, user_data.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )
    
    # Create user
    user_create = UserCreate(
        email=user_data.email,
        username=user_data.username,
        password=user_data.password,
        full_name=user_data.full_name,
        phone=user_data.phone,
        country=user_data.country,
    )
    new_user = await user_crud.create_user(db, user_create)
    
    # Send verification email if required
    if settings.REQUIRE_EMAIL_VERIFICATION:
        email_sent = await email_service.send_verification_email(
            to_email=new_user.email,
            verification_token=new_user.email_verification_token,
            username=new_user.username
        )
        
        if not email_sent:
            # Log email failure but don't fail registration
            await audit_crud.create_audit_log(
                db,
                user_id=new_user.id,
                action="email_verification_failed",
                resource_type="user",
                resource_id=str(new_user.id),
                ip_address=request.client.host if request.client else None,
                status="failed",
                error_message="Failed to send verification email"
            )
    
    # Create audit log
    await audit_crud.create_audit_log(
        db,
        user_id=new_user.id,
        action="user_registered",
        resource_type="user",
        resource_id=str(new_user.id),
        ip_address=request.client.host if request.client else None,
    )
    
    return new_user


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """User login"""
    
    # Get user by email
    user = await user_crud.get_user_by_email(db, credentials.email)
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        # Create failed login audit log
        await audit_crud.create_audit_log(
            db,
            user_id=user.id if user else None,
            action="login_failed",
            ip_address=request.client.host if request.client else None,
            status="failed",
            error_message="Invalid credentials",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )
    
    # Check email verification if required
    if settings.REQUIRE_EMAIL_VERIFICATION and not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email address before logging in. Check your inbox for verification email.",
        )
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Update last login
    await user_crud.update_last_login(db, user.id)
    
    # Create successful login audit log
    await audit_crud.create_audit_log(
        db,
        user_id=user.id,
        action="login_success",
        ip_address=request.client.host if request.client else None,
    )
    
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """Refresh access token"""
    
    try:
        # Decode refresh token
        payload = decode_token(token_data.refresh_token)
        user = await user_crud.get_user_by_id(db, payload.user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
        
        # Create new tokens
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        return Token(access_token=access_token, refresh_token=refresh_token)
        
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )


@router.get("/verify-email")
async def verify_email(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    """Verify user email address"""
    
    # Get user by verification token
    user = await user_crud.get_user_by_verification_token(db, token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token",
        )
    
    # Verify user email
    verified_user = await user_crud.verify_user_email(db, user.id)
    
    if not verified_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify email",
        )
    
    # Create audit log
    await audit_crud.create_audit_log(
        db,
        user_id=verified_user.id,
        action="email_verified",
        resource_type="user",
        resource_id=str(verified_user.id),
    )
    
    return {"message": "Email verified successfully! You can now log in to your account."}


@router.post("/logout")
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """User logout - creates audit log"""
    
    # Create logout audit log
    await audit_crud.create_audit_log(
        db,
        user_id=current_user.id,
        action="logout",
        resource_type="user",
        resource_id=str(current_user.id),
        ip_address=request.client.host if request.client else None,
    )
    
    return {"message": "Logged out successfully"}

