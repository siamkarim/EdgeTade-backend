"""
Trade CRUD operations
"""
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime, timedelta
import secrets

from app.models.trade import Trade
from app.schemas.trade import TradeStatistics


def generate_trade_id() -> str:
    """Generate unique trade ID"""
    return f"TRD{secrets.token_hex(8).upper()}"


async def create_trade(
    db: AsyncSession,
    account_id: int,
    order_id: str,
    symbol: str,
    side: str,
    volume: float,
    entry_price: float,
    exit_price: float,
    stop_loss: Optional[float],
    take_profit: Optional[float],
    profit_loss: float,
    profit_loss_pips: Optional[float],
    opened_at: datetime,
) -> Trade:
    """Create new trade (closed position)"""
    trade_id = generate_trade_id()
    
    duration = int((datetime.utcnow() - opened_at).total_seconds())
    
    db_trade = Trade(
        account_id=account_id,
        trade_id=trade_id,
        order_id=order_id,
        symbol=symbol,
        side=side,
        volume=volume,
        entry_price=entry_price,
        exit_price=exit_price,
        stop_loss=stop_loss,
        take_profit=take_profit,
        profit_loss=profit_loss,
        profit_loss_pips=profit_loss_pips,
        commission=0.0,  # Can be calculated based on broker
        swap=0.0,
        net_profit_loss=profit_loss,
        duration_seconds=duration,
        opened_at=opened_at,
    )
    
    db.add(db_trade)
    await db.commit()
    await db.refresh(db_trade)
    return db_trade


async def get_account_trades(
    db: AsyncSession,
    account_id: int,
    skip: int = 0,
    limit: int = 100,
) -> List[Trade]:
    """Get trades for an account"""
    result = await db.execute(
        select(Trade)
        .where(Trade.account_id == account_id)
        .order_by(Trade.closed_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def get_trades_by_date_range(
    db: AsyncSession,
    account_id: int,
    start_date: datetime,
    end_date: datetime,
) -> List[Trade]:
    """Get trades within a date range"""
    result = await db.execute(
        select(Trade)
        .where(
            Trade.account_id == account_id,
            Trade.closed_at >= start_date,
            Trade.closed_at <= end_date,
        )
        .order_by(Trade.closed_at.desc())
    )
    return result.scalars().all()


async def calculate_trade_statistics(
    db: AsyncSession, 
    account_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> TradeStatistics:
    """Calculate trade statistics for an account"""
    query = select(Trade).where(Trade.account_id == account_id)
    
    if start_date:
        query = query.where(Trade.closed_at >= start_date)
    if end_date:
        query = query.where(Trade.closed_at <= end_date)
    
    result = await db.execute(query)
    trades = result.scalars().all()
    
    if not trades:
        return TradeStatistics(
            total_trades=0,
            winning_trades=0,
            losing_trades=0,
            win_rate=0.0,
            total_pnl=0.0,
            average_win=0.0,
            average_loss=0.0,
            largest_win=0.0,
            largest_loss=0.0,
            profit_factor=0.0,
        )
    
    winning_trades = [t for t in trades if t.net_profit_loss > 0]
    losing_trades = [t for t in trades if t.net_profit_loss < 0]
    
    total_wins = sum(t.net_profit_loss for t in winning_trades)
    total_losses = abs(sum(t.net_profit_loss for t in losing_trades))
    
    return TradeStatistics(
        total_trades=len(trades),
        winning_trades=len(winning_trades),
        losing_trades=len(losing_trades),
        win_rate=len(winning_trades) / len(trades) * 100 if trades else 0.0,
        total_pnl=sum(t.net_profit_loss for t in trades),
        average_win=total_wins / len(winning_trades) if winning_trades else 0.0,
        average_loss=total_losses / len(losing_trades) if losing_trades else 0.0,
        largest_win=max((t.net_profit_loss for t in winning_trades), default=0.0),
        largest_loss=min((t.net_profit_loss for t in losing_trades), default=0.0),
        profit_factor=total_wins / total_losses if total_losses > 0 else 0.0,
        average_trade_duration=int(sum(t.duration_seconds or 0 for t in trades) / len(trades)) if trades else None,
    )

