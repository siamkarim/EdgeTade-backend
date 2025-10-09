"""
Main API Router - Aggregates all v1 routes
"""
from fastapi import APIRouter

from app.api.v1 import auth, users, accounts, orders, trades, admin, market

api_router = APIRouter()

# Include all route modules
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(accounts.router, prefix="/accounts", tags=["Trading Accounts"])
api_router.include_router(orders.router, prefix="/orders", tags=["Orders"])
api_router.include_router(trades.router, prefix="/trades", tags=["Trades"])
api_router.include_router(market.router, prefix="/market", tags=["Market Data"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])

