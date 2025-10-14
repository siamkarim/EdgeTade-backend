"""
Price Feed Service - Simulated price data for MVP
"""
import random
from typing import Dict, Optional
from datetime import datetime
import asyncio


class PriceFeedService:
    """
    Simulated price feed for MVP
    In production, this would connect to real broker APIs
    """
    
    def __init__(self):
        # Base prices for common forex pairs
        self.base_prices = {
            "EURUSD": 1.0850,
            "GBPUSD": 1.2650,
            "USDJPY": 149.50,
            "AUDUSD": 0.6550,
            "USDCAD": 1.3550,
            "USDCHF": 0.8850,
            "NZDUSD": 0.6050,
            "EURGBP": 0.8580,
            "EURJPY": 162.15,
            "GBPJPY": 189.10,
        }
        
        # Current prices with spread
        self.current_prices: Dict[str, Dict[str, float]] = {}
        self._initialize_prices()
    
    def _initialize_prices(self):
        """Initialize prices with bid/ask spread"""
        for symbol, base_price in self.base_prices.items():
            # Typical spread is 1-2 pips for major pairs
            spread_pips = 1.5
            pip_size = 0.01 if "JPY" in symbol else 0.0001
            spread = spread_pips * pip_size
            
            self.current_prices[symbol] = {
                "bid": base_price - (spread / 2),
                "ask": base_price + (spread / 2),
                "timestamp": datetime.utcnow(),
            }
    
    async def get_price(self, symbol: str) -> Optional[Dict[str, float]]:
        """Get current price for a symbol"""
        if symbol not in self.current_prices:
            return None
        
        # Simulate small price movement
        self._simulate_price_movement(symbol)
        
        return self.current_prices[symbol]
    
    def _simulate_price_movement(self, symbol: str):
        """Simulate realistic price movement"""
        if symbol not in self.current_prices:
            return
        
        current = self.current_prices[symbol]
        base_price = (current["bid"] + current["ask"]) / 2
        
        # Random walk with small movements
        pip_size = 0.01 if "JPY" in symbol else 0.0001
        max_movement_pips = 5  # Maximum 5 pip movement per update
        
        movement = random.uniform(-max_movement_pips, max_movement_pips) * pip_size
        new_base_price = base_price + movement
        
        # Update with spread
        spread_pips = 1.5
        spread = spread_pips * pip_size
        
        self.current_prices[symbol] = {
            "bid": new_base_price - (spread / 2),
            "ask": new_base_price + (spread / 2),
            "timestamp": datetime.utcnow(),
        }
    
    async def simulate_price_updates(self, interval_ms: int = 1000):
        """
        Continuously simulate price updates
        Run this as a background task
        """
        while True:
            for symbol in self.current_prices.keys():
                self._simulate_price_movement(symbol)
            
            await asyncio.sleep(interval_ms / 1000)
    
    def get_all_prices(self) -> Dict[str, Dict[str, float]]:
        """Get all current prices"""
        # Convert datetime objects to strings for JSON serialization
        result = {}
        for symbol, price_data in self.current_prices.items():
            result[symbol] = {
                "bid": price_data["bid"],
                "ask": price_data["ask"],
                "timestamp": price_data["timestamp"].isoformat() if isinstance(price_data["timestamp"], datetime) else str(price_data["timestamp"])
            }
        return result


# Singleton instance
price_feed_service = PriceFeedService()

