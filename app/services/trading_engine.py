"""
Trading Engine - Core trading logic and PnL calculation
"""
from typing import Dict, Optional, Tuple
from datetime import datetime
from loguru import logger

from app.models.order import OrderType, OrderSide, OrderStatus
from app.models.trading_account import TradingAccount
from app.services.price_feed import PriceFeedService


class TradingEngine:
    """Core trading engine for order execution and PnL calculation"""
    
    def __init__(self):
        self.price_feed = PriceFeedService()
    
    def calculate_pip_value(
        self, 
        symbol: str, 
        lot_size: float, 
        account_currency: str = "USD"
    ) -> float:
        """
        Calculate pip value dynamically based on symbol and lot size
        
        Formula: Pip Value = (Lot Size × Contract Size × Pip Size) × Exchange Rate
        Standard lot = 100,000 units
        """
        # Standard contract size
        contract_size = 100000
        
        # Most forex pairs have 0.0001 pip size (except JPY pairs: 0.01)
        pip_size = 0.01 if "JPY" in symbol else 0.0001
        
        # Calculate pip value in quote currency
        pip_value = (lot_size * contract_size * pip_size)
        
        # Convert to account currency if needed (simplified for now)
        # In production, you'd need real-time exchange rates
        return pip_value
    
    def calculate_pnl(
        self,
        symbol: str,
        side: OrderSide,
        entry_price: float,
        exit_price: float,
        lot_size: float,
        account_currency: str = "USD",
    ) -> Tuple[float, float]:
        """
        Calculate profit/loss for a trade
        
        Returns:
            Tuple of (pnl_in_currency, pnl_in_pips)
        """
        # Calculate price difference
        if side == OrderSide.BUY:
            price_diff = exit_price - entry_price
        else:  # SELL
            price_diff = entry_price - exit_price
        
        # Calculate pips
        pip_size = 0.01 if "JPY" in symbol else 0.0001
        pnl_pips = price_diff / pip_size
        
        # Calculate pip value
        pip_value = self.calculate_pip_value(symbol, lot_size, account_currency)
        
        # Calculate PnL in account currency
        pnl_currency = pnl_pips * pip_value
        
        return pnl_currency, pnl_pips
    
    def calculate_margin_required(
        self,
        symbol: str,
        lot_size: float,
        entry_price: float,
        leverage: int,
    ) -> float:
        """
        Calculate margin required for a position
        
        Formula: Used Margin = (Lots × Contract Size × Entry Price) / Leverage
        """
        contract_size = 100000
        position_value = lot_size * contract_size * entry_price
        margin_required = position_value / leverage
        
        return margin_required
    
    async def execute_market_order(
        self,
        symbol: str,
        side: OrderSide,
        quantity: float,
        account: TradingAccount,
    ) -> Tuple[bool, Optional[float], Optional[str]]:
        """
        Execute market order at current price
        
        Returns:
            Tuple of (success, execution_price, error_message)
        """
        try:
            # Get current market price
            current_price = await self.price_feed.get_price(symbol)
            
            if not current_price:
                return False, None, f"No price available for {symbol}"
            
            # Use bid for sell, ask for buy
            execution_price = current_price["ask"] if side == OrderSide.BUY else current_price["bid"]
            
            # Calculate margin required
            margin_required = self.calculate_margin_required(
                symbol, quantity, execution_price, account.leverage
            )
            
            # Check if sufficient margin available
            if margin_required > account.margin_free:
                return False, None, "Insufficient margin"
            
            return True, execution_price, None
            
        except Exception as e:
            logger.error(f"Error executing market order: {e}")
            return False, None, str(e)
    
    def check_limit_order_trigger(
        self,
        order_type: OrderType,
        side: OrderSide,
        order_price: float,
        current_price: Dict[str, float],
    ) -> bool:
        """Check if limit/stop order should be triggered"""
        
        if order_type == OrderType.LIMIT:
            if side == OrderSide.BUY:
                # Buy limit: trigger when ask <= order price
                return current_price["ask"] <= order_price
            else:  # SELL
                # Sell limit: trigger when bid >= order price
                return current_price["bid"] >= order_price
        
        elif order_type == OrderType.STOP:
            if side == OrderSide.BUY:
                # Buy stop: trigger when ask >= order price
                return current_price["ask"] >= order_price
            else:  # SELL
                # Sell stop: trigger when bid <= order price
                return current_price["bid"] <= order_price
        
        return False
    
    def check_stop_loss_hit(
        self,
        side: OrderSide,
        entry_price: float,
        stop_loss: float,
        current_price: Dict[str, float],
    ) -> bool:
        """Check if stop loss is hit"""
        if side == OrderSide.BUY:
            # For buy: stop loss is below entry, use bid price
            return current_price["bid"] <= stop_loss
        else:  # SELL
            # For sell: stop loss is above entry, use ask price
            return current_price["ask"] >= stop_loss
    
    def check_take_profit_hit(
        self,
        side: OrderSide,
        entry_price: float,
        take_profit: float,
        current_price: Dict[str, float],
    ) -> bool:
        """Check if take profit is hit"""
        if side == OrderSide.BUY:
            # For buy: take profit is above entry, use bid price
            return current_price["bid"] >= take_profit
        else:  # SELL
            # For sell: take profit is below entry, use ask price
            return current_price["ask"] <= take_profit


# Singleton instance
trading_engine = TradingEngine()

