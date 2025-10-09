"""
Risk & Margin Management Engine
"""
from typing import List, Dict, Optional
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.trading_account import TradingAccount
from app.models.order import Order, OrderStatus
from app.core.config import settings
from app.services.trading_engine import trading_engine
from app.services.price_feed import PriceFeedService


class RiskManager:
    """Risk and margin management system"""
    
    def __init__(self):
        self.price_feed = PriceFeedService()
        self.auto_liquidation_level = settings.AUTO_LIQUIDATION_MARGIN_LEVEL
        self.margin_call_level = settings.MARGIN_CALL_LEVEL
    
    async def calculate_account_metrics(
        self,
        account: TradingAccount,
        open_orders: List[Order],
    ) -> Dict[str, float]:
        """
        Calculate real-time account metrics
        
        Formulas:
        - Used Margin = Sum of margin for all open positions
        - Equity = Balance + Floating PnL
        - Free Margin = Equity - Used Margin
        - Margin Level = (Equity / Used Margin) × 100
        """
        balance = account.balance
        total_margin_used = 0.0
        total_floating_pnl = 0.0
        
        # Calculate for each open position
        for order in open_orders:
            if order.status != OrderStatus.OPEN:
                continue
            
            # Get current price
            current_price = await self.price_feed.get_price(order.symbol)
            if not current_price:
                continue
            
            # Calculate margin used for this position
            margin_used = trading_engine.calculate_margin_required(
                order.symbol,
                order.quantity,
                order.executed_price,
                account.leverage,
            )
            total_margin_used += margin_used
            
            # Calculate floating PnL
            exit_price = current_price["bid"] if order.side == "buy" else current_price["ask"]
            pnl, _ = trading_engine.calculate_pnl(
                order.symbol,
                order.side,
                order.executed_price,
                exit_price,
                order.quantity,
                account.currency.value,
            )
            total_floating_pnl += pnl
        
        # Calculate account metrics
        equity = balance + total_floating_pnl
        free_margin = equity - total_margin_used
        margin_level = (equity / total_margin_used * 100) if total_margin_used > 0 else 0.0
        
        return {
            "balance": balance,
            "equity": equity,
            "margin_used": total_margin_used,
            "margin_free": free_margin,
            "margin_level": margin_level,
            "floating_pnl": total_floating_pnl,
        }
    
    def check_margin_call(self, margin_level: float) -> bool:
        """Check if margin call should be triggered"""
        return margin_level < self.margin_call_level and margin_level > 0
    
    def check_auto_liquidation(self, margin_level: float) -> bool:
        """Check if positions should be auto-liquidated"""
        return margin_level < self.auto_liquidation_level and margin_level > 0
    
    def validate_new_order(
        self,
        account: TradingAccount,
        symbol: str,
        quantity: float,
        price: float,
    ) -> tuple[bool, Optional[str]]:
        """
        Validate if new order can be placed
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Calculate margin required for new order
        margin_required = trading_engine.calculate_margin_required(
            symbol,
            quantity,
            price,
            account.leverage,
        )
        
        # Check if sufficient free margin
        if margin_required > account.margin_free:
            return False, f"Insufficient margin. Required: {margin_required:.2f}, Available: {account.margin_free:.2f}"
        
        # Check if account is locked
        if account.is_locked:
            return False, "Account is locked"
        
        # Check if account is active
        if not account.is_active:
            return False, "Account is inactive"
        
        # Additional risk checks can be added here
        # - Maximum position size
        # - Maximum daily loss
        # - Maximum number of open positions
        
        return True, None
    
    async def get_positions_to_liquidate(
        self,
        open_orders: List[Order],
    ) -> List[Order]:
        """
        Determine which positions to close during auto-liquidation
        Strategy: Close positions with highest loss first
        """
        positions_with_pnl = []
        
        for order in open_orders:
            if order.status != OrderStatus.OPEN:
                continue
            
            # Get current price
            current_price = await self.price_feed.get_price(order.symbol)
            if not current_price:
                continue
            
            # Calculate current PnL
            exit_price = current_price["bid"] if order.side == "buy" else current_price["ask"]
            pnl, _ = trading_engine.calculate_pnl(
                order.symbol,
                order.side,
                order.executed_price,
                exit_price,
                order.quantity,
            )
            
            positions_with_pnl.append((order, pnl))
        
        # Sort by PnL (lowest first - biggest losers)
        positions_with_pnl.sort(key=lambda x: x[1])
        
        # Return all positions (close all during liquidation)
        return [pos[0] for pos in positions_with_pnl]


# Singleton instance
risk_manager = RiskManager()

