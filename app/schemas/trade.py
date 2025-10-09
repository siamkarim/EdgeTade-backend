"""
Trade schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.trade import TradeSide


class TradeResponse(BaseModel):
    """Trade response schema"""
    id: int
    account_id: int
    trade_id: str
    order_id: Optional[str] = None
    symbol: str
    side: TradeSide
    volume: float
    entry_price: float
    exit_price: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    profit_loss: float
    profit_loss_pips: Optional[float] = None
    commission: float
    swap: float
    net_profit_loss: float
    duration_seconds: Optional[int] = None
    opened_at: datetime
    closed_at: datetime
    
    class Config:
        from_attributes = True


class TradeListResponse(BaseModel):
    """Trade list response"""
    trades: list[TradeResponse]
    total: int
    page: int
    page_size: int
    
    # Summary statistics
    total_pnl: float = 0.0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: float = 0.0


class TradeStatistics(BaseModel):
    """Trade statistics schema"""
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_pnl: float
    average_win: float
    average_loss: float
    largest_win: float
    largest_loss: float
    profit_factor: float
    average_trade_duration: Optional[int] = None


class PerformanceReport(BaseModel):
    """Performance report schema"""
    period: str  # daily, weekly, monthly
    start_date: datetime
    end_date: datetime
    statistics: TradeStatistics
    trades: list[TradeResponse]

