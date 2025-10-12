# 🚀 EdgeTrade - Professional Forex Trading Platform

A professional-grade, scalable Forex trading platform built with FastAPI. Similar to FXPro, this platform supports real-time trading, order execution, risk management, and live P&L tracking.

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Installation](#installation)
- [API Documentation](#api-documentation)
- [WebSocket API](#websocket-api)
- [Database Schema](#database-schema)
- [Configuration](#configuration)
- [Broker Integration](#broker-integration)
- [Testing](#testing)
- [Deployment](#deployment)
- [Security](#security)
- [Contributing](#contributing)

## ✨ Features

### 1. User & Trading Account System
- ✅ JWT authentication with access & refresh tokens
- ✅ User registration/login with email verification
- ✅ Multiple trading accounts per user
- ✅ Demo and Live account modes
- ✅ Support for multiple currencies (USD, EUR, GBP, BTC)
- ✅ Configurable leverage (1:100, 1:500, etc.)
- ✅ Profile management with 2FA support
- ✅ KYC status tracking

### 2. Order Management System (OMS)
- ✅ **Market Orders** - Instant execution at current price
- ✅ **Limit Orders** - Execute at specified price or better
- ✅ **Stop Orders** - Trigger when price reaches threshold
- ✅ **Stop Loss (SL)** - Automatic loss protection
- ✅ **Take Profit (TP)** - Automatic profit taking
- ✅ **Trailing Stop** - Dynamic stop loss (optional)
- ✅ Order lifecycle: Pending → Open → Closed
- ✅ Modify/Cancel orders
- ✅ Complete order history with filtering

### 3. Real-time Trade Engine & PnL Calculation
- ✅ Dynamic pip value calculation based on symbol
- ✅ Real-time P&L calculation in account currency
- ✅ Formula: `Profit = (Close Price - Open Price) × Contract Size × Lots × Pip Value`
- ✅ Support for major forex pairs (EURUSD, GBPUSD, USDJPY, etc.)
- ✅ Accurate bid/ask spread handling

### 4. Risk & Margin Management Engine
- ✅ **Real-time calculations:**
  - Used Margin = `(Lots × Contract Size × Entry Price) / Leverage`
  - Equity = `Balance + Floating PnL`
  - Free Margin = `Equity - Used Margin`
  - Margin Level % = `(Equity / Used Margin) × 100`
- ✅ **Auto-Liquidation Logic:**
  - Automatically close all positions when Margin Level < 20%
- ✅ **Margin Call Alerts:**
  - WebSocket alerts when Margin Level < 50%
- ✅ Pre-order validation (sufficient margin check)

### 5. WebSocket Server for Real-time Sync
- ✅ Real-time price updates (simulated feed)
- ✅ Order status changes (filled, canceled, modified)
- ✅ Account balance, equity, margin updates
- ✅ Margin call alerts
- ✅ Auto-liquidation notifications
- ✅ Socket.IO implementation

### 6. Trade History & Reporting
- ✅ Store all closed trades with complete details
- ✅ Symbol, Volume, Entry/Exit prices, SL/TP
- ✅ P&L in currency and pips
- ✅ Trade duration tracking
- ✅ Performance reports (daily/weekly/monthly)
- ✅ Statistics: Win rate, profit factor, avg win/loss
- ✅ Export to CSV

### 7. Admin Panel APIs
- ✅ View/manage all users and accounts
- ✅ Activate/deactivate user accounts
- ✅ Manually adjust account balances
- ✅ System-wide metrics dashboard
- ✅ Audit logs for all critical actions
- ✅ Role-based access control

### 8. Security & Logging
- ✅ JWT authentication with refresh tokens
- ✅ Password hashing with bcrypt
- ✅ Rate limiting on all APIs
- ✅ Comprehensive audit logs (login, orders, withdrawals)
- ✅ Role-based access (User, Admin)
- ✅ IP address and user agent tracking

## 🛠️ Tech Stack

- **Framework:** FastAPI 0.109+
- **Database:** PostgreSQL with AsyncPG (or MongoDB)
- **Authentication:** JWT with python-jose
- **WebSocket:** Socket.IO (python-socketio)
- **ORM:** SQLAlchemy 2.0 (Async)
- **Caching:** Redis (optional)
- **Background Tasks:** Celery (optional)
- **Logging:** Loguru
- **Testing:** Pytest
- **Deployment:** Docker + Docker Compose

## 🏗️ Architecture

```
EdgeTrade-fastAPI/
├── app/
│   ├── api/                    # API routes
│   │   └── v1/
│   │       ├── auth.py         # Authentication endpoints
│   │       ├── users.py        # User management
│   │       ├── accounts.py     # Trading accounts
│   │       ├── orders.py       # Order management
│   │       ├── trades.py       # Trade history
│   │       ├── market.py       # Market data
│   │       └── admin.py        # Admin panel
│   ├── brokers/                # Broker abstraction layer
│   │   ├── base.py             # Abstract base class
│   │   ├── simulated.py        # Simulated broker
│   │   └── mt5.py              # MT5 integration
│   ├── core/                   # Core functionality
│   │   ├── config.py           # Configuration
│   │   ├── security.py         # Authentication & security
│   │   ├── database.py         # Database connection
│   │   └── logging.py          # Logging setup
│   ├── crud/                   # Database operations
│   │   ├── user.py
│   │   ├── trading_account.py
│   │   ├── order.py
│   │   ├── trade.py
│   │   └── audit_log.py
│   ├── models/                 # Database models
│   │   ├── user.py
│   │   ├── trading_account.py
│   │   ├── order.py
│   │   ├── trade.py
│   │   └── audit_log.py
│   ├── schemas/                # Pydantic schemas
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── trading_account.py
│   │   ├── order.py
│   │   └── trade.py
│   ├── services/               # Business logic
│   │   ├── trading_engine.py  # Trade execution & PnL
│   │   ├── risk_manager.py    # Risk & margin management
│   │   └── price_feed.py      # Price simulation
│   ├── websocket/              # WebSocket server
│   │   └── manager.py
│   ├── utils/                  # Utilities
│   │   └── rate_limiter.py
│   └── main.py                 # FastAPI app
├── main.py                     # Entry point
├── requirements.txt
├── .env.example
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## 📦 Installation

### Prerequisites
- Python 3.10+
- PostgreSQL 14+
- Redis (optional)

### 1. Clone the repository

```bash
git clone <repository-url>
cd EdgeTrade-fastAPI
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 5. Set up PostgreSQL

```bash
# Using Docker
docker run -d \
  --name edgetrade-db \
  -e POSTGRES_USER=edgetrade \
  -e POSTGRES_PASSWORD=edgetrade123 \
  -e POSTGRES_DB=edgetrade_db \
  -p 5432:5432 \
  postgres:14-alpine
```

### 6. Run Database Migration (if needed)

If you're upgrading from a previous version, run the email verification migration:

```bash
python scripts/migrate_email_verification.py
```

### 7. Run the application

```bash
python main.py
```

The API will be available at: `http://localhost:8000`

## 📧 Email Verification Workflow

EdgeTrade includes a complete email verification system for secure user registration:

### 1. User Registration
```bash
POST /api/v1/auth/register
{
  "email": "user@example.com",
  "username": "trader123",
  "password": "securepassword",
  "full_name": "John Doe",
  "phone": "+1234567890",
  "country": "USA"
}
```

**Response:** `201 Created` with `is_verified: false`

### 2. Email Verification
- Verification email is automatically sent to user's email
- Email contains verification link: `http://localhost:8000/api/v1/auth/verify-email?token=...`
- User clicks link to verify email address

### 3. Login After Verification
```bash
POST /api/v1/auth/login
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response:** JWT tokens for authenticated access

### 4. Create Trading Account
```bash
POST /api/v1/accounts/
Authorization: Bearer <jwt_token>
{
  "account_name": "My Trading Account",
  "account_type": "demo",
  "currency": "USD",
  "leverage": 100,
  "initial_balance": 10000.0
}
```

### Email Configuration
Configure SMTP settings in `.env` file for email delivery. Gmail App Passwords are recommended for production use.

## 📚 API Documentation

Once the application is running, access the interactive API documentation:

- **Swagger UI:** http://localhost:8000/api/docs
- **ReDoc:** http://localhost:8000/api/redoc
- **OpenAPI JSON:** http://localhost:8000/api/openapi.json

### Key Endpoints

#### Authentication
- `POST /api/v1/auth/register` - Register new user (with email verification)
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/verify-email` - Verify email address
- `POST /api/v1/auth/logout` - User logout

#### Trading Accounts
- `POST /api/v1/accounts/` - Create trading account
- `GET /api/v1/accounts/` - Get all accounts
- `GET /api/v1/accounts/{id}` - Get account details
- `GET /api/v1/accounts/{id}/balance` - Get real-time balance

#### Orders
- `POST /api/v1/orders/` - Place order
- `GET /api/v1/orders/` - Get orders
- `PUT /api/v1/orders/{id}` - Modify order
- `DELETE /api/v1/orders/{id}` - Cancel order
- `POST /api/v1/orders/{id}/close` - Close position

#### Trades
- `GET /api/v1/trades/` - Get trade history
- `GET /api/v1/trades/statistics` - Get trade statistics
- `GET /api/v1/trades/report` - Generate performance report
- `GET /api/v1/trades/export/csv` - Export trades to CSV

#### Market Data
- `GET /api/v1/market/symbols` - Available symbols
- `GET /api/v1/market/price/{symbol}` - Current price
- `GET /api/v1/market/prices` - All prices

## 🔌 WebSocket API

Connect to WebSocket: `ws://localhost:8000/ws/socket.io/`

### Events

#### Client → Server

```javascript
// Subscribe to price updates
socket.emit('subscribe_prices', {
  symbols: ['EURUSD', 'GBPUSD', 'USDJPY']
});

// Subscribe to account updates
socket.emit('subscribe_account', {
  account_id: 123
});
```

#### Server → Client

```javascript
// Price updates
socket.on('price_update', (data) => {
  // {symbol: 'EURUSD', bid: 1.0850, ask: 1.0852, timestamp: '...'}
});

// Order updates
socket.on('order_update', (data) => {
  // {order_id: 'ORD...', status: 'filled', ...}
});

// Account updates
socket.on('account_update', (data) => {
  // {balance: 10000, equity: 10050, margin_level: 150, ...}
});

// Alerts
socket.on('alert', (data) => {
  // {type: 'margin_call', message: '...', margin_level: 45}
});
```

## 🗄️ Database Schema

See detailed schema in `/docs/database_schema.md`

Key tables:
- `users` - User accounts
- `trading_accounts` - Trading accounts
- `orders` - All orders (pending, open, closed)
- `trades` - Closed positions (trade history)
- `audit_logs` - Security audit trail

## ⚙️ Configuration

Edit `.env` file for configuration:

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/dbname

# JWT
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Trading
SIMULATE_TRADING=True
AUTO_LIQUIDATION_MARGIN_LEVEL=20
MARGIN_CALL_LEVEL=50

# Email Verification
REQUIRE_EMAIL_VERIFICATION=True
SMTP_ENABLED=True
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=your-email@gmail.com
SMTP_TLS=True
```

## 🔗 Broker Integration

The platform uses a **pluggable broker architecture**. To add a new broker:

1. Create a new file in `app/brokers/` (e.g., `mt5.py`)
2. Implement the `BaseBroker` abstract class
3. Implement all required methods
4. Register the broker in the configuration

Example:

```python
from app.brokers.base import BaseBroker

class MT5Broker(BaseBroker):
    async def connect(self):
        # Connect to MT5 API
        pass
    
    async def place_order(self, ...):
        # Place order via MT5
        pass
    
    # ... implement other methods
```

Supported brokers:
- ✅ Simulated
- 🔄 MetaTrader 5 (MT5)
- 🔄 OANDA
- 🔄 Binance
- 🔄 Interactive Brokers

## 🧪 Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=app tests/

# Run specific test
pytest tests/test_orders.py
```

## 🚀 Deployment

### Using Docker

```bash
# Build image
docker build -t edgetrade-api .

# Run with docker-compose
docker-compose up -d
```

### Production Checklist
- [ ] Change `SECRET_KEY` in production
- [ ] Set `DEBUG=False`
- [ ] Configure proper CORS origins
- [ ] Set up SSL/TLS certificates
- [ ] Configure Redis for caching
- [ ] Set up monitoring (Sentry, DataDog)
- [ ] Enable database backups
- [ ] Configure rate limiting
- [ ] Set up CI/CD pipeline

## 🔒 Security

- JWT tokens with expiration
- Password hashing with bcrypt
- Rate limiting (60 requests/minute default)
- Audit logs for all critical actions
- Input validation with Pydantic
- SQL injection protection (ORM)
- CORS configuration
- Role-based access control


## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License.

## 📧 Support

For support, email: support@edgetrade.com

---

**Built with ❤️ using FastAPI**

