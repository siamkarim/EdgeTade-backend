# EdgeTrade Trading Platform API Documentation

## 🚀 Overview

The EdgeTrade API is a professional-grade Forex trading platform that provides real-time market data, order management, and risk management capabilities.

**Base URL:** `https://yourdomain.com/api/v1`  
**API Version:** 1.0.0  
**Documentation:** `https://yourdomain.com/api/docs`  
**ReDoc:** `https://yourdomain.com/api/redoc`

---

## 🔑 Authentication

The API uses JWT (JSON Web Token) authentication. Most endpoints require authentication.

### Getting Tokens

1. **Register** a new user account
2. **Verify** your email with the 6-digit code
3. **Login** to get access and refresh tokens

### Using Tokens

Include the access token in the Authorization header:

```http
Authorization: Bearer <your-access-token>
```

### Token Expiration

- **Access Token**: 30 minutes
- **Refresh Token**: 7 days

---

## 📊 API Endpoints

### 🔐 Authentication Endpoints

#### Register User
```http
POST /api/v1/auth/register
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "trader123",
  "password": "SecurePassword123!",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "country": "USA",
  "id_number": "123456789",
  "date_of_birth": "1990-01-01"
}
```

**Response (201):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "trader123",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "country": "USA",
  "id_number": "123456789",
  "date_of_birth": "1990-01-01T00:00:00Z",
  "is_active": true,
  "is_verified": false,
  "is_admin": false,
  "two_factor_enabled": false,
  "kyc_status": "pending",
  "created_at": "2025-01-15T10:30:00Z",
  "last_login": null
}
```

#### Login
```http
POST /api/v1/auth/login
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Send Email Verification Code
```http
POST /api/v1/auth/send-verification-code
```

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

#### Verify Email Code
```http
POST /api/v1/auth/verify-email-code
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "code": "123456"
}
```

#### Forgot Password
```http
POST /api/v1/auth/forgot-password
```

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

#### Reset Password
```http
POST /api/v1/auth/reset-password
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "code": "123456",
  "new_password": "NewSecurePassword123!"
}
```

---

### 👤 User Management

#### Get User Profile
```http
GET /api/v1/users/me
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "trader123",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "country": "USA",
  "id_number": "123456789",
  "date_of_birth": "1990-01-01T00:00:00Z",
  "is_active": true,
  "is_verified": true,
  "is_admin": false,
  "two_factor_enabled": false,
  "kyc_status": "pending",
  "created_at": "2025-01-15T10:30:00Z",
  "last_login": "2025-01-15T11:00:00Z"
}
```

#### Update User Profile
```http
PUT /api/v1/users/profile
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Smith",
  "phone": "+1987654321",
  "country": "Canada",
  "id_number": "987654321",
  "date_of_birth": "1985-05-15"
}
```

---

### 🏦 Trading Accounts

#### Create Trading Account
```http
POST /api/v1/accounts/
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "account_name": "My Demo Account",
  "account_type": "demo",
  "currency": "USD",
  "leverage": 100,
  "initial_balance": 10000.0
}
```

**Response (201):**
```json
{
  "id": 1,
  "user_id": 1,
  "account_name": "My Demo Account",
  "account_number": "EA1234567890",
  "account_type": "demo",
  "currency": "USD",
  "leverage": 100,
  "balance": 10000.0,
  "equity": 10000.0,
  "margin_used": 0.0,
  "margin_free": 10000.0,
  "margin_level": 0.0,
  "is_active": true,
  "created_at": "2025-01-15T10:30:00Z"
}
```

#### Get Trading Accounts
```http
GET /api/v1/accounts/
Authorization: Bearer <token>
```

#### Get Account Details
```http
GET /api/v1/accounts/{account_id}
Authorization: Bearer <token>
```

#### Get Account Balance
```http
GET /api/v1/accounts/{account_id}/balance
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "balance": 10000.0,
  "equity": 9975.50,
  "margin_used": 54.24,
  "margin_free": 9921.26,
  "margin_level": 18392.15,
  "unrealized_pnl": -24.50
}
```

---

### 📈 Market Data

#### Get Available Symbols
```http
GET /api/v1/market/symbols
Authorization: Bearer <token>
```

**Response (200):**
```json
[
  "EURUSD",
  "GBPUSD",
  "USDJPY",
  "AUDUSD",
  "USDCAD",
  "USDCHF",
  "NZDUSD",
  "EURGBP",
  "EURJPY",
  "GBPJPY"
]
```

#### Get Symbol Price
```http
GET /api/v1/market/price/{symbol}
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "symbol": "EURUSD",
  "bid": 1.08493,
  "ask": 1.08508,
  "timestamp": "2025-01-15T11:30:00Z"
}
```

#### Get Historical Data
```http
GET /api/v1/market/history/{symbol}?timeframe=1h&limit=100
Authorization: Bearer <token>
```

---

### 📋 Order Management

#### Place Order
```http
POST /api/v1/orders/
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "account_id": 1,
  "symbol": "EURUSD",
  "order_type": "market",
  "side": "buy",
  "quantity": 0.1,
  "stop_loss": 1.0800,
  "take_profit": 1.0900
}
```

**Response (201):**
```json
{
  "id": 1,
  "account_id": 1,
  "order_id": "ORD1234567890",
  "symbol": "EURUSD",
  "order_type": "market",
  "side": "buy",
  "quantity": 0.1,
  "filled_quantity": 0.1,
  "remaining_quantity": 0.0,
  "price": null,
  "executed_price": 1.08497,
  "stop_loss": 1.0800,
  "take_profit": 1.0900,
  "status": "open",
  "created_at": "2025-01-15T11:30:00Z"
}
```

#### Get Orders
```http
GET /api/v1/orders/?account_id=1&status=open
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "orders": [
    {
      "id": 1,
      "account_id": 1,
      "order_id": "ORD1234567890",
      "symbol": "EURUSD",
      "order_type": "market",
      "side": "buy",
      "quantity": 0.1,
      "filled_quantity": 0.1,
      "remaining_quantity": 0.0,
      "price": null,
      "executed_price": 1.08497,
      "stop_loss": 1.0800,
      "take_profit": 1.0900,
      "status": "open",
      "created_at": "2025-01-15T11:30:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 50
}
```

#### Modify Order
```http
PUT /api/v1/orders/{order_id}
Authorization: Bearer <token>
```

#### Cancel Order
```http
DELETE /api/v1/orders/{order_id}
Authorization: Bearer <token>
```

---

### 💰 Trade History

#### Get Trades
```http
GET /api/v1/trades/?account_id=1&page=1&page_size=50
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "trades": [
    {
      "id": 1,
      "account_id": 1,
      "trade_id": "TRD1234567890",
      "order_id": "ORD1234567890",
      "symbol": "EURUSD",
      "side": "buy",
      "volume": 0.1,
      "entry_price": 1.08497,
      "exit_price": 1.08950,
      "stop_loss": 1.0800,
      "take_profit": 1.0900,
      "pnl": 45.30,
      "commission": 0.0,
      "swap": 0.0,
      "status": "closed",
      "opened_at": "2025-01-15T11:30:00Z",
      "closed_at": "2025-01-15T12:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 50,
  "total_pnl": 45.30,
  "winning_trades": 1,
  "losing_trades": 0,
  "win_rate": 100.0
}
```

#### Get Trade Statistics
```http
GET /api/v1/trades/statistics?account_id=1
Authorization: Bearer <token>
```

---

## 🔌 WebSocket API

Connect to WebSocket for real-time updates:

```javascript
const ws = new WebSocket('wss://yourdomain.com/ws');

ws.onopen = function() {
    // Subscribe to market data
    ws.send(JSON.stringify({
        type: 'subscribe',
        channel: 'market_data',
        symbol: 'EURUSD'
    }));
    
    // Subscribe to account updates
    ws.send(JSON.stringify({
        type: 'subscribe',
        channel: 'account_updates',
        account_id: 1
    }));
};

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
};
```

### WebSocket Message Types

#### Market Data Update
```json
{
  "type": "market_data",
  "symbol": "EURUSD",
  "bid": 1.08493,
  "ask": 1.08508,
  "timestamp": "2025-01-15T11:30:00Z"
}
```

#### Order Update
```json
{
  "type": "order_update",
  "order_id": "ORD1234567890",
  "status": "filled",
  "executed_price": 1.08497,
  "timestamp": "2025-01-15T11:30:00Z"
}
```

#### Account Update
```json
{
  "type": "account_update",
  "account_id": 1,
  "balance": 10000.0,
  "equity": 9975.50,
  "margin_used": 54.24,
  "margin_free": 9921.26,
  "margin_level": 18392.15,
  "timestamp": "2025-01-15T11:30:00Z"
}
```

---

## 📝 Error Handling

### HTTP Status Codes

- **200**: Success
- **201**: Created
- **400**: Bad Request
- **401**: Unauthorized
- **403**: Forbidden
- **404**: Not Found
- **422**: Validation Error
- **500**: Internal Server Error

### Error Response Format

```json
{
  "detail": "Error message",
  "error_code": "ERROR_CODE",
  "timestamp": "2025-01-15T11:30:00Z"
}
```

### Common Error Codes

- `EMAIL_ALREADY_EXISTS`: Email is already registered
- `USERNAME_TAKEN`: Username is already taken
- `INVALID_CREDENTIALS`: Wrong email or password
- `EMAIL_NOT_VERIFIED`: Email verification required
- `ACCOUNT_INACTIVE`: User account is inactive
- `INSUFFICIENT_MARGIN`: Not enough margin for the order
- `INVALID_SYMBOL`: Trading symbol not supported
- `ORDER_NOT_FOUND`: Order does not exist
- `ACCOUNT_NOT_FOUND`: Trading account not found

---

## 🚀 Quick Start Guide

### 1. Register User
```bash
curl -X POST "https://yourdomain.com/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "trader@example.com",
    "username": "trader123",
    "password": "SecurePassword123!",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

### 2. Verify Email
```bash
curl -X POST "https://yourdomain.com/api/v1/auth/send-verification-code" \
  -H "Content-Type: application/json" \
  -d '{"email": "trader@example.com"}'

# Use the 6-digit code from email
curl -X POST "https://yourdomain.com/api/v1/auth/verify-email-code" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "trader@example.com",
    "code": "123456"
  }'
```

### 3. Login
```bash
curl -X POST "https://yourdomain.com/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "trader@example.com",
    "password": "SecurePassword123!"
  }'
```

### 4. Create Trading Account
```bash
curl -X POST "https://yourdomain.com/api/v1/accounts/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-access-token>" \
  -d '{
    "account_name": "My Demo Account",
    "account_type": "demo",
    "currency": "USD",
    "leverage": 100,
    "initial_balance": 10000.0
  }'
```

### 5. Place Order
```bash
curl -X POST "https://yourdomain.com/api/v1/orders/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-access-token>" \
  -d '{
    "account_id": 1,
    "symbol": "EURUSD",
    "order_type": "market",
    "side": "buy",
    "quantity": 0.1,
    "stop_loss": 1.0800,
    "take_profit": 1.0900
  }'
```

---

## 🔧 SDK Examples

### JavaScript/Node.js
```javascript
const axios = require('axios');

class EdgeTradeAPI {
  constructor(baseURL, token = null) {
    this.baseURL = baseURL;
    this.token = token;
  }
  
  setToken(token) {
    this.token = token;
  }
  
  async request(method, endpoint, data = null) {
    const config = {
      method,
      url: `${this.baseURL}${endpoint}`,
      headers: {
        'Content-Type': 'application/json',
      }
    };
    
    if (this.token) {
      config.headers.Authorization = `Bearer ${this.token}`;
    }
    
    if (data) {
      config.data = data;
    }
    
    return await axios(config);
  }
  
  async register(userData) {
    return await this.request('POST', '/auth/register', userData);
  }
  
  async login(email, password) {
    const response = await this.request('POST', '/auth/login', { email, password });
    this.setToken(response.data.access_token);
    return response;
  }
  
  async createAccount(accountData) {
    return await this.request('POST', '/accounts/', accountData);
  }
  
  async placeOrder(orderData) {
    return await this.request('POST', '/orders/', orderData);
  }
}

// Usage
const api = new EdgeTradeAPI('https://yourdomain.com/api/v1');

// Register and login
await api.register({
  email: 'trader@example.com',
  username: 'trader123',
  password: 'SecurePassword123!',
  first_name: 'John',
  last_name: 'Doe'
});

await api.login('trader@example.com', 'SecurePassword123!');

// Create account and place order
const account = await api.createAccount({
  account_name: 'My Demo Account',
  account_type: 'demo',
  currency: 'USD',
  leverage: 100,
  initial_balance: 10000.0
});

const order = await api.placeOrder({
  account_id: account.data.id,
  symbol: 'EURUSD',
  order_type: 'market',
  side: 'buy',
  quantity: 0.1
});
```

### Python
```python
import requests
import json

class EdgeTradeAPI:
    def __init__(self, base_url, token=None):
        self.base_url = base_url
        self.token = token
        self.session = requests.Session()
        
    def set_token(self, token):
        self.token = token
        self.session.headers.update({'Authorization': f'Bearer {token}'})
    
    def request(self, method, endpoint, data=None):
        url = f"{self.base_url}{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        
        response = self.session.request(method, url, json=data, headers=headers)
        response.raise_for_status()
        return response.json()
    
    def register(self, user_data):
        return self.request('POST', '/auth/register', user_data)
    
    def login(self, email, password):
        response = self.request('POST', '/auth/login', {'email': email, 'password': password})
        self.set_token(response['access_token'])
        return response
    
    def create_account(self, account_data):
        return self.request('POST', '/accounts/', account_data)
    
    def place_order(self, order_data):
        return self.request('POST', '/orders/', order_data)

# Usage
api = EdgeTradeAPI('https://yourdomain.com/api/v1')

# Register and login
api.register({
    'email': 'trader@example.com',
    'username': 'trader123',
    'password': 'SecurePassword123!',
    'first_name': 'John',
    'last_name': 'Doe'
})

api.login('trader@example.com', 'SecurePassword123!')

# Create account and place order
account = api.create_account({
    'account_name': 'My Demo Account',
    'account_type': 'demo',
    'currency': 'USD',
    'leverage': 100,
    'initial_balance': 10000.0
})

order = api.place_order({
    'account_id': account['id'],
    'symbol': 'EURUSD',
    'order_type': 'market',
    'side': 'buy',
    'quantity': 0.1
})
```

---

## 📞 Support

- **API Documentation**: `https://yourdomain.com/api/docs`
- **ReDoc**: `https://yourdomain.com/api/redoc`
- **Support Email**: support@edgetrade.com
- **GitHub**: https://github.com/siamkarim/EdgeTade-backend

---

## 📄 License

This API is licensed under the MIT License. See the LICENSE file for details.
