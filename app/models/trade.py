"""
Trade (Closed Position) model
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class TradeSide(str, enum.Enum):
    """Trade side enumeration"""
    BUY = "buy"
    SELL = "sell"


class Trade(Base):
    """Trade model - stores closed positions"""
    
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("trading_accounts.id"), nullable=False)
    
    # Trade identification
    trade_id = Column(String(50), unique=True, index=True, nullable=False)
    order_id = Column(String(50), index=True, nullable=True)  # Link to original order
    
    # Trade details
    symbol = Column(String(20), nullable=False, index=True)
    side = Column(SQLEnum(TradeSide), nullable=False)
    
    # Quantity
    volume = Column(Float, nullable=False)  # Lot size
    
    # Prices
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=False)
    stop_loss = Column(Float, nullable=True)
    take_profit = Column(Float, nullable=True)
    
    # PnL Calculation
    profit_loss = Column(Float, nullable=False)  # In account currency
    profit_loss_pips = Column(Float, nullable=True)  # In pips
    commission = Column(Float, default=0.0)
    swap = Column(Float, default=0.0)
    net_profit_loss = Column(Float, nullable=False)  # PnL - commission - swap
    
    # Trade metrics
    duration_seconds = Column(Integer, nullable=True)  # Trade duration
    
    # Additional info
    notes = Column(Text, nullable=True)
    
    # Timestamps
    opened_at = Column(DateTime(timezone=True), nullable=False)
    closed_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    account = relationship("TradingAccount", back_populates="trades")
    
    def __repr__(self):
        return f"<Trade(id={self.id}, trade_id={self.trade_id}, symbol={self.symbol}, pnl={self.net_profit_loss})>"

