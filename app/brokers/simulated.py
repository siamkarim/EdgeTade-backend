"""
Simulated Broker - For MVP without real broker connection
"""
from typing import Dict, List, Optional
from datetime import datetime

from app.brokers.base import BaseBroker
from app.services.price_feed import price_feed_service


class SimulatedBroker(BaseBroker):
    """Simulated broker for testing and MVP"""
    
    def __init__(self, api_key: str = "simulated", api_secret: Optional[str] = None):
        super().__init__(api_key, api_secret)
        self.account_balance = 10000.0
        self.open_positions = []
    
    async def connect(self) -> bool:
        """Connect to simulated broker"""
        self.is_connected = True
        return True
    
    async def disconnect(self) -> bool:
        """Disconnect from simulated broker"""
        self.is_connected = False
        return True
    
    async def get_account_info(self) -> Dict:
        """Get simulated account information"""
        return {
            "balance": self.account_balance,
            "equity": self.account_balance,
            "margin_used": 0.0,
            "margin_free": self.account_balance,
            "margin_level": 0.0,
        }
    
    async def get_price(self, symbol: str) -> Optional[Dict[str, float]]:
        """Get price from simulated price feed"""
        return await price_feed_service.get_price(symbol)
    
    async def place_order(
        self,
        symbol: str,
        order_type: str,
        side: str,
        quantity: float,
        price: Optional[float] = None,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
    ) -> Dict:
        """Place simulated order"""
        current_price = await self.get_price(symbol)
        
        if not current_price:
            return {"success": False, "error": "Symbol not found"}
        
        execution_price = current_price["ask"] if side == "buy" else current_price["bid"]
        
        return {
            "success": True,
            "order_id": f"SIM_{datetime.utcnow().timestamp()}",
            "status": "filled",
            "execution_price": execution_price,
        }
    
    async def modify_order(
        self,
        order_id: str,
        price: Optional[float] = None,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
    ) -> bool:
        """Modify simulated order"""
        return True
    
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel simulated order"""
        return True
    
    async def close_position(self, position_id: str) -> Dict:
        """Close simulated position"""
        return {
            "success": True,
            "execution_price": 0.0,
            "pnl": 0.0,
        }
    
    async def get_open_positions(self) -> List[Dict]:
        """Get simulated open positions"""
        return self.open_positions
    
    async def get_order_history(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Dict]:
        """Get simulated order history"""
        return []
    
    async def get_available_symbols(self) -> List[str]:
        """Get available symbols"""
        return list(price_feed_service.base_prices.keys())


# Example of how to add MT5 broker integration (placeholder for future)
# from app.brokers.mt5 import MT5Broker
# from app.brokers.oanda import OandaBroker
# from app.brokers.binance import BinanceBroker

