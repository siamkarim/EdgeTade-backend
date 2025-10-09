"""
Application configuration
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache
import json


class Settings(BaseSettings):
    """Application settings - All values can be overridden via .env file"""
    
    # ========== Application Settings ==========
    APP_NAME: str = "EdgeTrade Trading Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"  # development, staging, production
    TIMEZONE: str = "UTC"
    
    # ========== Server Settings ==========
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True  # Auto-reload on code changes (dev only)
    WORKERS: int = 1  # Number of worker processes (production)
    
    # ========== Database Settings ==========
    DATABASE_URL: str = "postgresql+asyncpg://postgres:admin@localhost:5432/edgetrade_db"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_ECHO: bool = False  # Set True to see SQL queries
    
    # ========== JWT Authentication ==========
    SECRET_KEY: str = "your-secret-key-change-this-in-production-use-openssl-rand-hex-32"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # ========== Redis Cache ==========
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_ENABLED: bool = False  # Set True when Redis is available
    CACHE_EXPIRE_SECONDS: int = 300  # 5 minutes
    
    # ========== CORS (Cross-Origin Resource Sharing) ==========
    CORS_ORIGINS: str = '["http://localhost:3000","http://localhost:8080","http://127.0.0.1:3000"]'
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from JSON string"""
        try:
            return json.loads(self.CORS_ORIGINS)
        except:
            return ["http://localhost:3000"]
    
    # ========== Security & Rate Limiting ==========
    RATE_LIMIT_PER_MINUTE: int = 60
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 15
    
    # ========== Trading Settings ==========
    SIMULATE_TRADING: bool = True  # Use simulated prices (False = real broker)
    PRICE_UPDATE_INTERVAL_MS: int = 1000  # Price update frequency
    DEFAULT_LEVERAGE: int = 100  # 1:100 leverage
    MAX_LEVERAGE: int = 500  # Maximum allowed leverage
    MIN_LOT_SIZE: float = 0.01  # Minimum trade size
    MAX_LOT_SIZE: float = 100.0  # Maximum trade size
    
    # ========== Risk Management ==========
    AUTO_LIQUIDATION_MARGIN_LEVEL: float = 20.0  # Auto-close positions below 20%
    MARGIN_CALL_LEVEL: float = 50.0  # Alert user below 50%
    MAX_OPEN_POSITIONS: int = 50  # Max positions per account
    DEFAULT_STOP_LOSS_PIPS: int = 50  # Default SL if not specified
    DEFAULT_TAKE_PROFIT_PIPS: int = 100  # Default TP if not specified
    
    # ========== Admin Credentials ==========
    ADMIN_EMAIL: str = "admin@edgetrade.com"
    ADMIN_PASSWORD: str = "admin"
    ADMIN_USERNAME: str = "admin"
    
    # ========== Logging ==========
    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_FILE: str = "logs/app.log"
    LOG_ROTATION: str = "10 MB"  # Rotate log file at 10 MB
    LOG_RETENTION: str = "30 days"  # Keep logs for 30 days
    LOG_FORMAT: str = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"
    
    # ========== WebSocket ==========
    WS_HEARTBEAT_INTERVAL: int = 30  # Ping interval in seconds
    WS_MESSAGE_QUEUE_SIZE: int = 100
    WS_MAX_CONNECTIONS: int = 1000
    
    # ========== Pagination ==========
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # ========== File Upload ==========
    MAX_UPLOAD_SIZE_MB: int = 10
    UPLOAD_DIR: str = "uploads"
    ALLOWED_EXTENSIONS: List[str] = ["jpg", "jpeg", "png", "pdf"]
    
    # ========== Email Settings (Optional) ==========
    SMTP_ENABLED: bool = False
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM: Optional[str] = "noreply@edgetrade.com"
    SMTP_TLS: bool = True
    
    # ========== Broker API Integration (Future) ==========
    # MetaTrader 5
    MT5_ENABLED: bool = False
    MT5_API_KEY: Optional[str] = None
    MT5_API_SECRET: Optional[str] = None
    MT5_ACCOUNT_ID: Optional[str] = None
    
    # OANDA
    OANDA_ENABLED: bool = False
    OANDA_API_KEY: Optional[str] = None
    OANDA_ACCOUNT_ID: Optional[str] = None
    OANDA_PRACTICE: bool = True  # True = demo, False = live
    
    # Binance
    BINANCE_ENABLED: bool = False
    BINANCE_API_KEY: Optional[str] = None
    BINANCE_API_SECRET: Optional[str] = None
    BINANCE_TESTNET: bool = True  # True = testnet, False = mainnet
    
    # ========== Monitoring & Analytics ==========
    SENTRY_DSN: Optional[str] = None  # Error tracking
    SENTRY_ENABLED: bool = False
    DATADOG_API_KEY: Optional[str] = None  # Performance monitoring
    DATADOG_ENABLED: bool = False
    
    # ========== Feature Flags ==========
    ENABLE_WEBSOCKET: bool = True
    ENABLE_ADMIN_PANEL: bool = True
    ENABLE_API_DOCS: bool = True
    ENABLE_ANALYTICS: bool = True
    REQUIRE_EMAIL_VERIFICATION: bool = False
    REQUIRE_KYC: bool = False  # Know Your Customer
    
    # ========== Market Data ==========
    MARKET_DATA_CACHE_SECONDS: int = 1
    HISTORICAL_DATA_DAYS: int = 365  # How many days of history to keep
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = True
        
    def get_database_url(self) -> str:
        """Get database URL"""
        return self.DATABASE_URL
    
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.ENVIRONMENT.lower() == "production"
    
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.ENVIRONMENT.lower() == "development"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance
    
    Returns:
        Settings: Application settings
    """
    return Settings()


# Global settings instance
settings = get_settings()


# Helper functions
def reload_settings():
    """Reload settings (clears cache)"""
    get_settings.cache_clear()
    return get_settings()

