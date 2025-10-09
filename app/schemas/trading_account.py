"""
Trading Account schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.trading_account import AccountType, AccountCurrency


class TradingAccountCreate(BaseModel):
    """Trading account creation schema"""
    account_name: str
    account_type: AccountType = AccountType.DEMO
    currency: AccountCurrency = AccountCurrency.USD
    leverage: int = 100
    initial_balance: float = 10000.0


class TradingAccountUpdate(BaseModel):
    """Trading account update schema"""
    account_name: Optional[str] = None
    leverage: Optional[int] = None
    is_active: Optional[bool] = None


class TradingAccountResponse(BaseModel):
    """Trading account response schema"""
    id: int
    user_id: int
    account_name: str
    account_number: str
    account_type: AccountType
    currency: AccountCurrency
    leverage: int
    balance: float
    equity: float
    margin_used: float
    margin_free: float
    margin_level: float
    is_active: bool
    is_locked: bool
    created_at: datetime
    last_activity: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AccountBalance(BaseModel):
    """Account balance information"""
    balance: float
    equity: float
    margin_used: float
    margin_free: float
    margin_level: float
    unrealized_pnl: float = 0.0

