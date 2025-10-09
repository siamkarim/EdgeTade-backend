"""
Trading Account endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.trading_account import (
    TradingAccountCreate,
    TradingAccountUpdate,
    TradingAccountResponse,
    AccountBalance,
)
from app.crud import trading_account as account_crud
from app.crud import order as order_crud
from app.models.order import OrderStatus
from app.services.risk_manager import risk_manager

router = APIRouter()


@router.post("/", response_model=TradingAccountResponse, status_code=status.HTTP_201_CREATED)
async def create_trading_account(
    account_data: TradingAccountCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new trading account"""
    new_account = await account_crud.create_trading_account(db, current_user.id, account_data)
    return new_account


@router.get("/", response_model=List[TradingAccountResponse])
async def get_user_trading_accounts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all trading accounts for current user"""
    accounts = await account_crud.get_user_trading_accounts(db, current_user.id)
    return accounts


@router.get("/{account_id}", response_model=TradingAccountResponse)
async def get_trading_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get specific trading account"""
    account = await account_crud.get_trading_account_by_id(db, account_id)
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trading account not found",
        )
    
    if account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this account",
        )
    
    return account


@router.put("/{account_id}", response_model=TradingAccountResponse)
async def update_trading_account(
    account_id: int,
    account_data: TradingAccountUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update trading account"""
    account = await account_crud.get_trading_account_by_id(db, account_id)
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trading account not found",
        )
    
    if account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this account",
        )
    
    updated_account = await account_crud.update_trading_account(db, account_id, account_data)
    return updated_account


@router.get("/{account_id}/balance", response_model=AccountBalance)
async def get_account_balance(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get real-time account balance and margin information"""
    account = await account_crud.get_trading_account_by_id(db, account_id)
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trading account not found",
        )
    
    if account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this account",
        )
    
    # Get open orders
    open_orders = await order_crud.get_account_orders(db, account_id, status=OrderStatus.OPEN)
    
    # Calculate real-time metrics
    metrics = await risk_manager.calculate_account_metrics(account, open_orders)
    
    return AccountBalance(
        balance=metrics["balance"],
        equity=metrics["equity"],
        margin_used=metrics["margin_used"],
        margin_free=metrics["margin_free"],
        margin_level=metrics["margin_level"],
        unrealized_pnl=metrics["floating_pnl"],
    )

