"""
Order model
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class OrderType(str, enum.Enum):
    """Order type enumeration"""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"


class OrderSide(str, enum.Enum):
    """Order side enumeration"""
    BUY = "buy"
    SELL = "sell"


class OrderStatus(str, enum.Enum):
    """Order status enumeration"""
    PENDING = "pending"
    OPEN = "open"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"


class Order(Base):
    """Order model"""
    
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("trading_accounts.id"), nullable=False)
    
    # Order identification
    order_id = Column(String(50), unique=True, index=True, nullable=False)
    client_order_id = Column(String(100), nullable=True)
    
    # Order details
    symbol = Column(String(20), nullable=False, index=True)  # EURUSD, GBPUSD, etc.
    order_type = Column(SQLEnum(OrderType), nullable=False)
    side = Column(SQLEnum(OrderSide), nullable=False)
    
    # Quantity
    quantity = Column(Float, nullable=False)  # Lot size (e.g., 0.01, 0.1, 1.0)
    filled_quantity = Column(Float, default=0.0)
    remaining_quantity = Column(Float, nullable=False)
    
    # Prices
    price = Column(Float, nullable=True)  # Entry price for limit/stop orders
    stop_loss = Column(Float, nullable=True)
    take_profit = Column(Float, nullable=True)
    trailing_stop = Column(Float, nullable=True)  # Distance in pips
    
    # Execution
    executed_price = Column(Float, nullable=True)  # Actual execution price
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING, index=True)
    
    # Risk and margin
    margin_required = Column(Float, nullable=True)
    
    # Additional info
    notes = Column(Text, nullable=True)
    rejection_reason = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    filled_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    account = relationship("TradingAccount", back_populates="orders")
    
    def __repr__(self):
        return f"<Order(id={self.id}, order_id={self.order_id}, symbol={self.symbol}, status={self.status})>"

