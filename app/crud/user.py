"""
User CRUD operations
"""
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime, timedelta
import secrets

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    """Get user by ID"""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Get user by email"""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """Get user by username"""
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
    """Create new user"""
    hashed_password = get_password_hash(user_data.password)
    
    # Generate email verification token
    verification_token = secrets.token_urlsafe(32)
    verification_expires = datetime.utcnow() + timedelta(hours=24)
    
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        phone=user_data.phone,
        country=user_data.country,
        email_verification_token=verification_token,
        email_verification_expires=verification_expires,
        is_verified=False,  # User needs to verify email
    )
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def update_user(db: AsyncSession, user_id: int, user_data: UserUpdate) -> Optional[User]:
    """Update user"""
    stmt = (
        update(User)
        .where(User.id == user_id)
        .values(**user_data.model_dump(exclude_unset=True))
        .returning(User)
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.scalar_one_or_none()


async def update_last_login(db: AsyncSession, user_id: int) -> None:
    """Update user's last login timestamp"""
    stmt = update(User).where(User.id == user_id).values(last_login=datetime.utcnow())
    await db.execute(stmt)
    await db.commit()


async def get_all_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[User]:
    """Get all users (admin function)"""
    result = await db.execute(select(User).offset(skip).limit(limit))
    return result.scalars().all()


async def get_user_by_verification_token(db: AsyncSession, token: str) -> Optional[User]:
    """Get user by email verification token"""
    result = await db.execute(
        select(User).where(
            User.email_verification_token == token,
            User.email_verification_expires > datetime.utcnow()
        )
    )
    return result.scalar_one_or_none()


async def verify_user_email(db: AsyncSession, user_id: int) -> Optional[User]:
    """Mark user email as verified"""
    stmt = (
        update(User)
        .where(User.id == user_id)
        .values(
            is_verified=True,
            email_verification_token=None,
            email_verification_expires=None
        )
        .returning(User)
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.scalar_one_or_none()

