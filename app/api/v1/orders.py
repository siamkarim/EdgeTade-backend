"""
Order Management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.order import OrderStatus, OrderType
from app.schemas.order import OrderCreate, OrderModify, OrderResponse, OrderListResponse
from app.crud import order as order_crud
from app.crud import trading_account as account_crud
from app.crud import audit_log as audit_crud
from app.services.trading_engine import trading_engine
from app.services.risk_manager import risk_manager
from app.services.price_feed import price_feed_service

router = APIRouter()


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def place_order(
    order_data: OrderCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Place a new order"""
    
    # Verify account ownership
    account = await account_crud.get_trading_account_by_id(db, order_data.account_id)
    if not account or account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to trade on this account",
        )
    
    # Validate order price for limit/stop orders
    if order_data.order_type in [OrderType.LIMIT, OrderType.STOP]:
        if not order_data.price:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Price is required for {order_data.order_type} orders",
            )
        price_to_check = order_data.price
    else:
        # For market orders, get current price
        current_price = await price_feed_service.get_price(order_data.symbol)
        if not current_price:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Symbol {order_data.symbol} not available",
            )
        price_to_check = current_price["ask"] if order_data.side == "buy" else current_price["bid"]
    
    # Validate risk
    is_valid, error_msg = risk_manager.validate_new_order(
        account,
        order_data.symbol,
        order_data.quantity,
        price_to_check,
    )
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg,
        )
    
    # Create order
    new_order = await order_crud.create_order(db, order_data)
    
    # Execute market orders immediately
    if order_data.order_type == OrderType.MARKET:
        success, execution_price, error = await trading_engine.execute_market_order(
            order_data.symbol,
            order_data.side,
            order_data.quantity,
            account,
        )
        
        if success:
            await order_crud.update_order_status(
                db,
                new_order.id,
                OrderStatus.OPEN,
                executed_price=execution_price,
                filled_quantity=order_data.quantity,
            )
        else:
            await order_crud.update_order_status(
                db,
                new_order.id,
                OrderStatus.REJECTED,
                rejection_reason=error,
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error,
            )
    
    # Create audit log
    await audit_crud.create_audit_log(
        db,
        user_id=current_user.id,
        action="order_placed",
        resource_type="order",
        resource_id=new_order.order_id,
        ip_address=request.client.host if request.client else None,
        details={"symbol": order_data.symbol, "side": order_data.side, "quantity": order_data.quantity},
    )
    
    # Refresh to get updated data
    await db.refresh(new_order)
    return new_order


@router.get("/", response_model=OrderListResponse)
async def get_orders(
    account_id: int,
    status: Optional[OrderStatus] = None,
    page: int = 1,
    page_size: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get orders for an account"""
    
    # Verify account ownership
    account = await account_crud.get_trading_account_by_id(db, account_id)
    if not account or account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this account",
        )
    
    skip = (page - 1) * page_size
    orders = await order_crud.get_account_orders(db, account_id, status, skip, page_size)
    
    return OrderListResponse(
        orders=orders,
        total=len(orders),
        page=page,
        page_size=page_size,
    )


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get specific order details"""
    
    order = await order_crud.get_order_by_order_id(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
    
    # Verify ownership through account
    account = await account_crud.get_trading_account_by_id(db, order.account_id)
    if not account or account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this order",
        )
    
    return order


@router.put("/{order_id}", response_model=OrderResponse)
async def modify_order(
    order_id: str,
    order_data: OrderModify,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Modify an existing order"""
    
    order = await order_crud.get_order_by_order_id(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
    
    # Verify ownership
    account = await account_crud.get_trading_account_by_id(db, order.account_id)
    if not account or account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this order",
        )
    
    # Can only modify pending or open orders
    if order.status not in [OrderStatus.PENDING, OrderStatus.OPEN]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot modify order with status {order.status}",
        )
    
    updated_order = await order_crud.modify_order(db, order.id, order_data)
    
    # Create audit log
    await audit_crud.create_audit_log(
        db,
        user_id=current_user.id,
        action="order_modified",
        resource_type="order",
        resource_id=order_id,
        ip_address=request.client.host if request.client else None,
    )
    
    return updated_order


@router.delete("/{order_id}")
async def cancel_order(
    order_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Cancel an order"""
    
    order = await order_crud.get_order_by_order_id(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
    
    # Verify ownership
    account = await account_crud.get_trading_account_by_id(db, order.account_id)
    if not account or account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to cancel this order",
        )
    
    # Can only cancel pending orders
    if order.status != OrderStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel order with status {order.status}",
        )
    
    await order_crud.cancel_order(db, order.id)
    
    # Create audit log
    await audit_crud.create_audit_log(
        db,
        user_id=current_user.id,
        action="order_cancelled",
        resource_type="order",
        resource_id=order_id,
        ip_address=request.client.host if request.client else None,
    )
    
    return {"message": "Order cancelled successfully"}


@router.post("/{order_id}/close")
async def close_position(
    order_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Close an open position"""
    
    order = await order_crud.get_order_by_order_id(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
    
    # Verify ownership
    account = await account_crud.get_trading_account_by_id(db, order.account_id)
    if not account or account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to close this position",
        )
    
    # Can only close open orders
    if order.status != OrderStatus.OPEN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order is not open",
        )
    
    # Get current price for closing
    current_price = await price_feed_service.get_price(order.symbol)
    if not current_price:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to get current price",
        )
    
    # Calculate exit price (opposite of entry)
    exit_price = current_price["bid"] if order.side == "buy" else current_price["ask"]
    
    # Calculate PnL
    pnl, pnl_pips = trading_engine.calculate_pnl(
        order.symbol,
        order.side,
        order.executed_price,
        exit_price,
        order.quantity,
        account.currency.value,
    )
    
    # Update order status to filled/closed
    await order_crud.update_order_status(db, order.id, OrderStatus.FILLED)
    
    # Create trade record
    from app.crud import trade as trade_crud
    await trade_crud.create_trade(
        db,
        account_id=account.id,
        order_id=order.order_id,
        symbol=order.symbol,
        side=order.side,
        volume=order.quantity,
        entry_price=order.executed_price,
        exit_price=exit_price,
        stop_loss=order.stop_loss,
        take_profit=order.take_profit,
        profit_loss=pnl,
        profit_loss_pips=pnl_pips,
        opened_at=order.filled_at,
    )
    
    # Update account balance
    new_balance = account.balance + pnl
    await account_crud.update_account_balance(
        db,
        account.id,
        balance=new_balance,
        equity=new_balance,
        margin_used=0.0,
        margin_free=new_balance,
        margin_level=0.0,
    )
    
    # Create audit log
    await audit_crud.create_audit_log(
        db,
        user_id=current_user.id,
        action="position_closed",
        resource_type="order",
        resource_id=order_id,
        ip_address=request.client.host if request.client else None,
        details={"pnl": pnl, "exit_price": exit_price},
    )
    
    return {
        "message": "Position closed successfully",
        "exit_price": exit_price,
        "pnl": pnl,
        "pnl_pips": pnl_pips,
    }

