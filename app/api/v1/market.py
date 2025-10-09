"""
Market Data endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict

from app.core.security import get_current_user
from app.models.user import User
from app.services.price_feed import price_feed_service

router = APIRouter()


@router.get("/symbols", response_model=List[str])
async def get_available_symbols(
    current_user: User = Depends(get_current_user),
):
    """Get list of available trading symbols"""
    return list(price_feed_service.base_prices.keys())


@router.get("/price/{symbol}")
async def get_symbol_price(
    symbol: str,
    current_user: User = Depends(get_current_user),
):
    """Get current price for a symbol"""
    price = await price_feed_service.get_price(symbol)
    
    if not price:
        raise HTTPException(
            status_code=404,
            detail=f"Symbol {symbol} not found",
        )
    
    return price


@router.get("/prices")
async def get_all_prices(
    current_user: User = Depends(get_current_user),
) -> Dict[str, Dict[str, float]]:
    """Get current prices for all symbols"""
    return price_feed_service.get_all_prices()

