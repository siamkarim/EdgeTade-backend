"""
Order schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.order import OrderType, OrderSide, OrderStatus


class OrderCreate(BaseModel):
    """Order creation schema"""
    account_id: int
    symbol: str = Field(..., min_length=6, max_length=20)
    order_type: OrderType
    side: OrderSide
    quantity: float = Field(..., gt=0)
    price: Optional[float] = None  # Required for limit/stop orders
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    trailing_stop: Optional[float] = None
    notes: Optional[str] = None


class OrderModify(BaseModel):
    """Order modification schema"""
    price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    trailing_stop: Optional[float] = None
    quantity: Optional[float] = None


class OrderResponse(BaseModel):
    """Order response schema"""
    id: int
    account_id: int
    order_id: str
    symbol: str
    order_type: OrderType
    side: OrderSide
    quantity: float
    filled_quantity: float
    remaining_quantity: float
    price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    trailing_stop: Optional[float] = None
    executed_price: Optional[float] = None
    status: OrderStatus
    margin_required: Optional[float] = None
    created_at: datetime
    filled_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    """Order list response"""
    orders: list[OrderResponse]
    total: int
    page: int
    page_size: int

