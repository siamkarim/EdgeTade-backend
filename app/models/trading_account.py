"""
Trading Account model
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class AccountType(str, enum.Enum):
    """Account type enumeration"""
    DEMO = "demo"
    LIVE = "live"


class AccountCurrency(str, enum.Enum):
    """Account currency enumeration"""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    BTC = "BTC"


class TradingAccount(Base):
    """Trading Account model"""
    
    __tablename__ = "trading_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Account details
    account_name = Column(String(255), nullable=False)
    account_number = Column(String(50), unique=True, index=True, nullable=False)
    account_type = Column(SQLEnum(AccountType), default=AccountType.DEMO)
    
    # Currency and leverage
    currency = Column(SQLEnum(AccountCurrency), default=AccountCurrency.USD)
    leverage = Column(Integer, default=100)  # 1:100, 1:500, etc.
    
    # Balance and equity
    balance = Column(Float, default=10000.0)
    equity = Column(Float, default=10000.0)
    
    # Margin
    margin_used = Column(Float, default=0.0)
    margin_free = Column(Float, default=10000.0)
    margin_level = Column(Float, default=0.0)  # Percentage
    
    # Status
    is_active = Column(Boolean, default=True)
    is_locked = Column(Boolean, default=False)
    
    # Broker connection (for future integration)
    broker_name = Column(String(100), nullable=True)
    broker_account_id = Column(String(255), nullable=True)
    broker_api_key = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_activity = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="trading_accounts")
    orders = relationship("Order", back_populates="account", cascade="all, delete-orphan")
    trades = relationship("Trade", back_populates="account", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<TradingAccount(id={self.id}, account_number={self.account_number}, type={self.account_type})>"

