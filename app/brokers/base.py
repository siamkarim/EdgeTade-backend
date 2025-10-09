"""
Base Broker Interface - Abstract class for broker integrations
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datetime import datetime


class BaseBroker(ABC):
    """
    Abstract base class for broker integrations
    All broker implementations must inherit from this class
    """
    
    def __init__(self, api_key: str, api_secret: Optional[str] = None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.is_connected = False
    
    @abstractmethod
    async def connect(self) -> bool:
        """Connect to broker API"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """Disconnect from broker API"""
        pass
    
    @abstractmethod
    async def get_account_info(self) -> Dict:
        """
        Get account information
        Returns: {balance, equity, margin_used, margin_free, margin_level}
        """
        pass
    
    @abstractmethod
    async def get_price(self, symbol: str) -> Optional[Dict[str, float]]:
        """
        Get current price for a symbol
        Returns: {bid, ask, timestamp}
        """
        pass
    
    @abstractmethod
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
        """
        Place an order
        Returns: {order_id, status, execution_price}
        """
        pass
    
    @abstractmethod
    async def modify_order(
        self,
        order_id: str,
        price: Optional[float] = None,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
    ) -> bool:
        """Modify an existing order"""
        pass
    
    @abstractmethod
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an order"""
        pass
    
    @abstractmethod
    async def close_position(self, position_id: str) -> Dict:
        """
        Close an open position
        Returns: {success, execution_price, pnl}
        """
        pass
    
    @abstractmethod
    async def get_open_positions(self) -> List[Dict]:
        """Get all open positions"""
        pass
    
    @abstractmethod
    async def get_order_history(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Dict]:
        """Get order history"""
        pass
    
    @abstractmethod
    async def get_available_symbols(self) -> List[str]:
        """Get list of available trading symbols"""
        pass

