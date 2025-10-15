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
from app.schemas.user import (
    UserResponse, UserCreate, 
    PasswordResetRequest, PasswordResetVerify, PasswordResetUpdate,
    EmailVerificationRequest, EmailVerificationVerify
)
from app.crud import user as user_crud
from app.crud import audit_log as audit_crud
from app.services.email_service import email_service
from app.core.config import settings
from app.models.user import User

router = APIRouter()


@router.post(
    "/register", 
    response_model=UserResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Register New User",
    description="""
    Register a new user account with the EdgeTrade platform.
    
    **Required Fields:**
    - `email`: Valid email address (must be unique)
    - `username`: Unique username (3-50 characters)
    - `password`: Strong password (min 8 characters)
    
    **Optional Fields:**
    - `first_name`: User's first name
    - `last_name`: User's last name
    - `phone`: Phone number with country code
    - `country`: Country of residence
    - `id_number`: ID number (optional)
    - `date_of_birth`: Date of birth (YYYY-MM-DD format)
    
    **Response:**
    Returns user information with `is_verified: false`. User must verify email before login.
    
    **Email Verification:**
    After registration, a 6-digit verification code is sent to the user's email.
    Use `/send-verification-code` and `/verify-email-code` to complete verification.
    """,
    responses={
        201: {
            "description": "User registered successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "email": "user@example.com",
                        "username": "trader123",
                        "first_name": "John",
                        "last_name": "Doe",
                        "phone": "+1234567890",
                        "country": "USA",
                        "id_number": "123456789",
                        "date_of_birth": "1990-01-01T00:00:00Z",
                        "is_active": True,
                        "is_verified": False,
                        "is_admin": False,
                        "two_factor_enabled": False,
                        "kyc_status": "pending",
                        "created_at": "2025-01-15T10:30:00Z",
                        "last_login": None
                    }
                }
            }
        },
        400: {
            "description": "Registration failed",
            "content": {
                "application/json": {
                    "examples": {
                        "email_exists": {
                            "summary": "Email already registered",
                            "value": {"detail": "Email already registered"}
                        },
                        "username_taken": {
                            "summary": "Username already taken",
                            "value": {"detail": "Username already taken"}
                        },
                        "invalid_date": {
                            "summary": "Invalid date format",
                            "value": {"detail": "Invalid date of birth format. Use YYYY-MM-DD."}
                        }
                    }
                }
            }
        }
    }
)
async def register(
    user_data: UserRegister,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user account"""
    
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
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone=user_data.phone,
        country=user_data.country,
        id_number=user_data.id_number,
        date_of_birth=user_data.date_of_birth,
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


@router.post(
    "/login", 
    response_model=Token,
    summary="User Login",
    description="""
    Authenticate user and get JWT tokens for API access.
    
    **Required Fields:**
    - `email`: User's email address
    - `password`: User's password
    
    **Response:**
    Returns access token and refresh token. Access token expires in 30 minutes.
    
    **Token Usage:**
    Include the access token in the Authorization header for protected endpoints:
    ```
    Authorization: Bearer <access_token>
    ```
    
    **Email Verification:**
    Users must verify their email before they can log in.
    """,
    responses={
        200: {
            "description": "Login successful",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer"
                    }
                }
            }
        },
        401: {
            "description": "Authentication failed",
            "content": {
                "application/json": {
                    "examples": {
                        "invalid_credentials": {
                            "summary": "Invalid email or password",
                            "value": {"detail": "Incorrect email or password"}
                        },
                        "email_not_verified": {
                            "summary": "Email not verified",
                            "value": {"detail": "Please verify your email address before logging in. Check your inbox for verification email."}
                        },
                        "account_inactive": {
                            "summary": "Account inactive",
                            "value": {"detail": "Account is inactive"}
                        }
                    }
                }
            }
        }
    }
)
async def login(
    credentials: UserLogin,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate user and return JWT tokens"""
    
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


# Email Verification Code Endpoints
@router.post("/send-verification-code")
async def send_verification_code(
    request_data: EmailVerificationRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Send email verification code"""
    
    user = await user_crud.get_user_by_email(db, request_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified",
        )
    
    # Generate verification code
    verification_code = await user_crud.generate_email_verification_code(db, request_data.email)
    if not verification_code:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate verification code",
        )
    
    # Send verification code email
    await email_service.send_verification_code_email(
        request_data.email, 
        verification_code, 
        user.username
    )
    
    return {"message": "Verification code sent to your email"}


@router.post("/verify-email-code")
async def verify_email_code(
    request_data: EmailVerificationVerify,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Verify email with 6-digit code"""
    
    success = await user_crud.verify_email_code(db, request_data.email, request_data.code)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification code",
        )
    
    user = await user_crud.get_user_by_email(db, request_data.email)
    
    # Create audit log
    try:
        await audit_crud.create_audit_log(
            db,
            user_id=user.id,
            action="email_verified_code",
            resource_type="user",
            resource_id=str(user.id),
            ip_address=request.client.host if request.client else None,
        )
    except Exception as e:
        print(f"Audit log error: {e}")
    
    return {"message": "Email verified successfully! You can now log in to your account."}


# Password Reset Endpoints
@router.post("/forgot-password")
async def forgot_password(
    request_data: PasswordResetRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Send password reset code"""
    
    user = await user_crud.get_user_by_email(db, request_data.email)
    if not user:
        # Don't reveal if user exists or not for security
        return {"message": "If the email exists, a reset code has been sent"}
    
    # Generate reset code
    reset_code = await user_crud.generate_password_reset_code(db, request_data.email)
    if not reset_code:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate reset code",
        )
    
    # Send reset code email
    await email_service.send_password_reset_code_email(
        request_data.email, 
        reset_code, 
        user.username
    )
    
    # Create audit log
    await audit_crud.create_audit_log(
        db,
        user_id=user.id,
        action="password_reset_requested",
        resource_type="user",
        resource_id=str(user.id),
        ip_address=request.client.host if request.client else None,
    )
    
    return {"message": "If the email exists, a reset code has been sent"}


@router.post("/verify-reset-code")
async def verify_reset_code(
    request_data: PasswordResetVerify,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Verify password reset code"""
    
    success = await user_crud.verify_password_reset_code(db, request_data.email, request_data.code)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset code",
        )
    
    return {"message": "Reset code verified successfully"}


@router.post("/reset-password")
async def reset_password(
    request_data: PasswordResetUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Reset password with verification code"""
    
    success = await user_crud.reset_password_with_code(
        db, 
        request_data.email, 
        request_data.code, 
        request_data.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset code",
        )
    
    user = await user_crud.get_user_by_email(db, request_data.email)
    
    # Create audit log
    await audit_crud.create_audit_log(
        db,
        user_id=user.id,
        action="password_reset_completed",
        resource_type="user",
        resource_id=str(user.id),
        ip_address=request.client.host if request.client else None,
    )
    
    return {"message": "Password reset successfully"}

