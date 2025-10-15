"""
Main FastAPI application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.v1.router import api_router
from app.websocket.manager import socket_app
from app.core.database import init_db

# Setup logging
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    await init_db()
    yield
    # Shutdown
    pass


# Create FastAPI app with comprehensive documentation
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    ## 🚀 EdgeTrade Trading Platform API

    A professional-grade Forex trading platform with real-time market data, order management, and risk management.

    ### 🔑 Authentication
    Most endpoints require JWT authentication. Include the token in the Authorization header:
    ```
    Authorization: Bearer <your-jwt-token>
    ```

    ### 📊 Key Features
    - **User Management**: Registration, login, email verification, password reset
    - **Trading Accounts**: Create and manage demo/live trading accounts
    - **Order Management**: Place market, limit, stop orders with risk management
    - **Real-time Data**: Live market prices and WebSocket updates
    - **Risk Management**: Margin calculation, stop loss, take profit
    - **Audit Logging**: Complete transaction history and security logs

    ### 🎯 Getting Started
    1. **Register**: Create a new user account
    2. **Verify Email**: Complete email verification with 6-digit code
    3. **Login**: Get JWT access and refresh tokens
    4. **Create Account**: Set up a trading account
    5. **Start Trading**: Place orders and monitor positions

    ### 📈 Trading Flow
    1. Get market symbols: `GET /api/v1/market/symbols`
    2. Get current prices: `GET /api/v1/market/price/{symbol}`
    3. Place order: `POST /api/v1/orders/`
    4. Monitor positions: `GET /api/v1/orders/?account_id={id}`
    5. View trades: `GET /api/v1/trades/?account_id={id}`

    ### 🔒 Security
    - JWT-based authentication
    - Email verification required
    - Rate limiting enabled
    - Audit logging for all actions
    - CORS protection

    ### 📱 WebSocket Support
    Connect to `/ws` for real-time updates:
    - Market price updates
    - Order status changes
    - Account balance updates
    - Trade notifications
    """,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
    contact={
        "name": "EdgeTrade Support",
        "email": "support@edgetrade.com",
        "url": "https://edgetrade.com/support",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    servers=[
        {
            "url": "https://yourdomain.com",
            "description": "Production server"
        },
        {
            "url": "http://localhost:8000",
            "description": "Development server"
        }
    ],
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Mount Socket.IO
app.mount("/ws", socket_app)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/api/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

