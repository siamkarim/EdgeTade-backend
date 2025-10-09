"""
Trade History and Reporting endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.trade import TradeResponse, TradeListResponse, TradeStatistics, PerformanceReport
from app.crud import trading_account as account_crud
from app.crud import trade as trade_crud

router = APIRouter()


@router.get("/", response_model=TradeListResponse)
async def get_trades(
    account_id: int,
    page: int = 1,
    page_size: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get trade history for an account"""
    
    # Verify account ownership
    account = await account_crud.get_trading_account_by_id(db, account_id)
    if not account or account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this account",
        )
    
    skip = (page - 1) * page_size
    trades = await trade_crud.get_account_trades(db, account_id, skip, page_size)
    
    # Calculate summary statistics
    total_pnl = sum(t.net_profit_loss for t in trades)
    winning_trades = len([t for t in trades if t.net_profit_loss > 0])
    losing_trades = len([t for t in trades if t.net_profit_loss < 0])
    win_rate = (winning_trades / len(trades) * 100) if trades else 0.0
    
    return TradeListResponse(
        trades=trades,
        total=len(trades),
        page=page,
        page_size=page_size,
        total_pnl=total_pnl,
        winning_trades=winning_trades,
        losing_trades=losing_trades,
        win_rate=win_rate,
    )


@router.get("/statistics", response_model=TradeStatistics)
async def get_trade_statistics(
    account_id: int,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get trade statistics for an account"""
    
    # Verify account ownership
    account = await account_crud.get_trading_account_by_id(db, account_id)
    if not account or account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this account",
        )
    
    statistics = await trade_crud.calculate_trade_statistics(
        db, account_id, start_date, end_date
    )
    
    return statistics


@router.get("/report", response_model=PerformanceReport)
async def get_performance_report(
    account_id: int,
    period: str = Query("daily", regex="^(daily|weekly|monthly)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate performance report"""
    
    # Verify account ownership
    account = await account_crud.get_trading_account_by_id(db, account_id)
    if not account or account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this account",
        )
    
    # Calculate date range based on period
    end_date = datetime.utcnow()
    if period == "daily":
        start_date = end_date - timedelta(days=1)
    elif period == "weekly":
        start_date = end_date - timedelta(weeks=1)
    else:  # monthly
        start_date = end_date - timedelta(days=30)
    
    # Get trades and statistics
    trades = await trade_crud.get_trades_by_date_range(db, account_id, start_date, end_date)
    statistics = await trade_crud.calculate_trade_statistics(db, account_id, start_date, end_date)
    
    return PerformanceReport(
        period=period,
        start_date=start_date,
        end_date=end_date,
        statistics=statistics,
        trades=trades,
    )


@router.get("/export/csv")
async def export_trades_to_csv(
    account_id: int,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Export trades to CSV (optional feature)"""
    
    # Verify account ownership
    account = await account_crud.get_trading_account_by_id(db, account_id)
    if not account or account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this account",
        )
    
    # Get trades
    if start_date and end_date:
        trades = await trade_crud.get_trades_by_date_range(db, account_id, start_date, end_date)
    else:
        trades = await trade_crud.get_account_trades(db, account_id, skip=0, limit=10000)
    
    # Convert to CSV format (simplified)
    csv_data = "Trade ID,Symbol,Side,Volume,Entry Price,Exit Price,P/L,P/L Pips,Commission,Swap,Net P/L,Opened At,Closed At\n"
    
    for trade in trades:
        csv_data += f"{trade.trade_id},{trade.symbol},{trade.side},{trade.volume},{trade.entry_price},{trade.exit_price},"
        csv_data += f"{trade.profit_loss},{trade.profit_loss_pips},{trade.commission},{trade.swap},{trade.net_profit_loss},"
        csv_data += f"{trade.opened_at},{trade.closed_at}\n"
    
    from fastapi.responses import Response
    
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=trades_{account_id}_{datetime.utcnow().strftime('%Y%m%d')}.csv"
        },
    )

