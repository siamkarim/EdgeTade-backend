"""
Admin Panel endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.core.security import get_current_admin_user
from app.models.user import User
from app.schemas.user import UserResponse
from app.crud import user as user_crud
from app.crud import trading_account as account_crud
from app.crud import audit_log as audit_crud
from app.models.audit_log import AuditLog
from sqlalchemy import update

router = APIRouter()


@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all users (admin only)"""
    users = await user_crud.get_all_users(db, skip, limit)
    return users


@router.post("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Deactivate a user account"""
    user = await user_crud.get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    stmt = update(User).where(User.id == user_id).values(is_active=False)
    await db.execute(stmt)
    await db.commit()
    
    return {"message": f"User {user.email} deactivated successfully"}


@router.post("/users/{user_id}/activate")
async def activate_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Activate a user account"""
    user = await user_crud.get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    stmt = update(User).where(User.id == user_id).values(is_active=True)
    await db.execute(stmt)
    await db.commit()
    
    return {"message": f"User {user.email} activated successfully"}


@router.post("/accounts/{account_id}/adjust-balance")
async def adjust_account_balance(
    account_id: int,
    new_balance: float,
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Manually adjust account balance (for MVP testing)"""
    account = await account_crud.get_trading_account_by_id(db, account_id)
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
        )
    
    await account_crud.update_account_balance(
        db,
        account_id,
        balance=new_balance,
        equity=new_balance,
        margin_used=account.margin_used,
        margin_free=new_balance - account.margin_used,
        margin_level=account.margin_level,
    )
    
    # Create audit log
    await audit_crud.create_audit_log(
        db,
        user_id=current_admin.id,
        action="balance_adjusted",
        resource_type="account",
        resource_id=str(account_id),
        details={"old_balance": account.balance, "new_balance": new_balance},
    )
    
    return {"message": "Balance adjusted successfully", "new_balance": new_balance}


@router.get("/audit-logs")
async def get_audit_logs(
    action: str = None,
    skip: int = 0,
    limit: int = 100,
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Get audit logs (admin only)"""
    logs = await audit_crud.get_all_audit_logs(db, action, skip, limit)
    return logs


@router.get("/system/metrics")
async def get_system_metrics(
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Get system-wide metrics"""
    from sqlalchemy import select, func
    from app.models.trading_account import TradingAccount
    from app.models.order import Order
    from app.models.trade import Trade
    
    # Count users
    user_count_result = await db.execute(select(func.count(User.id)))
    total_users = user_count_result.scalar()
    
    # Count accounts
    account_count_result = await db.execute(select(func.count(TradingAccount.id)))
    total_accounts = account_count_result.scalar()
    
    # Count open orders
    open_orders_result = await db.execute(
        select(func.count(Order.id)).where(Order.status == "open")
    )
    open_orders = open_orders_result.scalar()
    
    # Count total trades
    trades_count_result = await db.execute(select(func.count(Trade.id)))
    total_trades = trades_count_result.scalar()
    
    # Calculate total PnL
    total_pnl_result = await db.execute(select(func.sum(Trade.net_profit_loss)))
    total_pnl = total_pnl_result.scalar() or 0.0
    
    return {
        "total_users": total_users,
        "total_accounts": total_accounts,
        "open_orders": open_orders,
        "total_trades": total_trades,
        "total_platform_pnl": total_pnl,
    }

