"""
Order CRUD operations
"""
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
import secrets
from datetime import datetime

from app.models.order import Order, OrderStatus
from app.schemas.order import OrderCreate, OrderModify


def generate_order_id() -> str:
    """Generate unique order ID"""
    return f"ORD{secrets.token_hex(8).upper()}"


async def create_order(db: AsyncSession, order_data: OrderCreate) -> Order:
    """Create new order"""
    order_id = generate_order_id()
    
    db_order = Order(
        account_id=order_data.account_id,
        order_id=order_id,
        symbol=order_data.symbol,
        order_type=order_data.order_type,
        side=order_data.side,
        quantity=order_data.quantity,
        remaining_quantity=order_data.quantity,
        price=order_data.price,
        stop_loss=order_data.stop_loss,
        take_profit=order_data.take_profit,
        trailing_stop=order_data.trailing_stop,
        notes=order_data.notes,
        status=OrderStatus.PENDING,
    )
    
    db.add(db_order)
    await db.commit()
    await db.refresh(db_order)
    return db_order


async def get_order_by_id(db: AsyncSession, order_id: int) -> Optional[Order]:
    """Get order by ID"""
    result = await db.execute(select(Order).where(Order.id == order_id))
    return result.scalar_one_or_none()


async def get_order_by_order_id(db: AsyncSession, order_id: str) -> Optional[Order]:
    """Get order by order_id string"""
    result = await db.execute(select(Order).where(Order.order_id == order_id))
    return result.scalar_one_or_none()


async def get_account_orders(
    db: AsyncSession,
    account_id: int,
    status: Optional[OrderStatus] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[Order]:
    """Get orders for an account"""
    query = select(Order).where(Order.account_id == account_id)
    
    if status:
        query = query.where(Order.status == status)
    
    query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


async def update_order_status(
    db: AsyncSession,
    order_id: int,
    status: OrderStatus,
    executed_price: Optional[float] = None,
    filled_quantity: Optional[float] = None,
    rejection_reason: Optional[str] = None,
) -> Optional[Order]:
    """Update order status"""
    update_data = {"status": status}
    
    if executed_price:
        update_data["executed_price"] = executed_price
    if filled_quantity is not None:
        update_data["filled_quantity"] = filled_quantity
        update_data["remaining_quantity"] = Order.quantity - filled_quantity
    if status == OrderStatus.FILLED:
        update_data["filled_at"] = datetime.utcnow()
    if status == OrderStatus.CANCELLED:
        update_data["cancelled_at"] = datetime.utcnow()
    if rejection_reason:
        update_data["rejection_reason"] = rejection_reason
    
    stmt = (
        update(Order)
        .where(Order.id == order_id)
        .values(**update_data)
        .returning(Order)
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.scalar_one_or_none()


async def modify_order(
    db: AsyncSession, 
    order_id: int, 
    order_data: OrderModify
) -> Optional[Order]:
    """Modify existing order"""
    stmt = (
        update(Order)
        .where(Order.id == order_id)
        .values(**order_data.model_dump(exclude_unset=True))
        .returning(Order)
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.scalar_one_or_none()


async def cancel_order(db: AsyncSession, order_id: int) -> Optional[Order]:
    """Cancel an order"""
    return await update_order_status(db, order_id, OrderStatus.CANCELLED)

