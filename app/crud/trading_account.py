"""
Trading Account CRUD operations
"""
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
import secrets

from app.models.trading_account import TradingAccount
from app.schemas.trading_account import TradingAccountCreate, TradingAccountUpdate


def generate_account_number() -> str:
    """Generate unique account number"""
    return f"EA{secrets.token_hex(6).upper()}"


async def create_trading_account(
    db: AsyncSession, 
    user_id: int, 
    account_data: TradingAccountCreate
) -> TradingAccount:
    """Create new trading account"""
    account_number = generate_account_number()
    
    db_account = TradingAccount(
        user_id=user_id,
        account_name=account_data.account_name,
        account_number=account_number,
        account_type=account_data.account_type,
        currency=account_data.currency,
        leverage=account_data.leverage,
        balance=account_data.initial_balance,
        equity=account_data.initial_balance,
        margin_free=account_data.initial_balance,
    )
    
    db.add(db_account)
    await db.commit()
    await db.refresh(db_account)
    return db_account


async def get_trading_account_by_id(
    db: AsyncSession, 
    account_id: int
) -> Optional[TradingAccount]:
    """Get trading account by ID"""
    result = await db.execute(
        select(TradingAccount).where(TradingAccount.id == account_id)
    )
    return result.scalar_one_or_none()


async def get_user_trading_accounts(
    db: AsyncSession, 
    user_id: int
) -> List[TradingAccount]:
    """Get all trading accounts for a user"""
    result = await db.execute(
        select(TradingAccount).where(TradingAccount.user_id == user_id)
    )
    return result.scalars().all()


async def update_trading_account(
    db: AsyncSession, 
    account_id: int, 
    account_data: TradingAccountUpdate
) -> Optional[TradingAccount]:
    """Update trading account"""
    stmt = (
        update(TradingAccount)
        .where(TradingAccount.id == account_id)
        .values(**account_data.model_dump(exclude_unset=True))
        .returning(TradingAccount)
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.scalar_one_or_none()


async def update_account_balance(
    db: AsyncSession,
    account_id: int,
    balance: float,
    equity: float,
    margin_used: float,
    margin_free: float,
    margin_level: float,
) -> None:
    """Update account balance and margin information"""
    stmt = (
        update(TradingAccount)
        .where(TradingAccount.id == account_id)
        .values(
            balance=balance,
            equity=equity,
            margin_used=margin_used,
            margin_free=margin_free,
            margin_level=margin_level,
        )
    )
    await db.execute(stmt)
    await db.commit()

