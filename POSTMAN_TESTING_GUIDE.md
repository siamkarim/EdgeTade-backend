# 🚀 EdgeTrade API - Postman Collection Guide

## 📋 **Complete API Testing Guide**

This guide provides step-by-step instructions for testing all EdgeTrade API endpoints using the provided Postman collection.

---

## 🔧 **Setup Instructions**

### **1. Import Collection & Environment**
1. **Import Collection**: `EdgeTrade_API_Collection.postman_collection.json`
2. **Import Environment**: `EdgeTrade_API_Environment.postman_environment.json`
3. **Select Environment**: Choose "EdgeTrade API Environment"

### **2. Configure Base URL**
- **Development**: `http://localhost:8000`
- **Production**: `https://yourdomain.com`

---

## 🎯 **Complete API Testing Workflow**

### **Step 1: User Registration**
```json
POST /api/v1/auth/register
{
  "email": "{{test_email}}",
  "username": "{{test_username}}",
  "password": "{{test_password}}",
  "first_name": "{{test_first_name}}",
  "last_name": "{{test_last_name}}",
  "phone": "{{test_phone}}",
  "country": "{{test_country}}",
  "id_number": "{{test_id_number}}",
  "date_of_birth": "{{test_date_of_birth}}"
}
```

**Expected Response:**
```json
{
  "id": 1,
  "email": "trader@example.com",
  "username": "trader123",
  "first_name": "John",
  "last_name": "Doe",
  "is_verified": false,
  "created_at": "2025-01-15T10:30:00Z"
}
```

### **Step 2: Email Verification**
```json
POST /api/v1/auth/send-verification-code
{
  "email": "{{test_email}}"
}
```

```json
POST /api/v1/auth/verify-email-code
{
  "email": "{{test_email}}",
  "verification_code": "{{verification_code}}"
}
```

### **Step 3: User Login**
```json
POST /api/v1/auth/login
{
  "email": "{{test_email}}",
  "password": "{{test_password}}"
}
```

**Expected Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**⚠️ Important**: Copy the `access_token` to the environment variable `{{access_token}}`

### **Step 4: Get User Profile**
```json
GET /api/v1/users/me
Authorization: Bearer {{access_token}}
```

### **Step 5: Create Trading Account**
```json
POST /api/v1/accounts/
Authorization: Bearer {{access_token}}
{
  "account_name": "{{account_name}}",
  "account_type": "{{account_type}}",
  "initial_balance": {{initial_balance}},
  "currency": "{{currency}}",
  "leverage": {{leverage}},
  "risk_level": "{{risk_level}}"
}
```

**Expected Response:**
```json
{
  "id": 1,
  "account_name": "My Demo Account",
  "account_type": "demo",
  "balance": 10000.00,
  "currency": "USD",
  "leverage": 100,
  "risk_level": "medium",
  "is_active": true,
  "created_at": "2025-01-15T10:30:00Z"
}
```

**⚠️ Important**: Copy the account `id` to the environment variable `{{account_id}}`

### **Step 6: Get Market Data**
```json
GET /api/v1/market/symbols
Authorization: Bearer {{access_token}}
```

```json
GET /api/v1/market/price/EURUSD
Authorization: Bearer {{access_token}}
```

### **Step 7: Place Orders**

#### **Market Order**
```json
POST /api/v1/orders/
Authorization: Bearer {{access_token}}
{
  "account_id": {{account_id}},
  "symbol": "{{symbol}}",
  "order_type": "market",
  "side": "{{order_side}}",
  "quantity": {{quantity}},
  "stop_loss": {{stop_loss}},
  "take_profit": {{take_profit}}
}
```

#### **Limit Order**
```json
POST /api/v1/orders/
Authorization: Bearer {{access_token}}
{
  "account_id": {{account_id}},
  "symbol": "{{symbol}}",
  "order_type": "limit",
  "side": "{{order_side}}",
  "quantity": {{quantity}},
  "price": {{price}},
  "stop_loss": {{stop_loss}},
  "take_profit": {{take_profit}}
}
```

#### **Stop Order**
```json
POST /api/v1/orders/
Authorization: Bearer {{access_token}}
{
  "account_id": {{account_id}},
  "symbol": "{{symbol}}",
  "order_type": "stop",
  "side": "sell",
  "quantity": {{quantity}},
  "price": {{price}},
  "stop_loss": {{stop_loss}},
  "take_profit": {{take_profit}}
}
```

### **Step 8: Order Management**

#### **Get Orders**
```json
GET /api/v1/orders/?account_id={{account_id}}&status=active&limit=50
Authorization: Bearer {{access_token}}
```

#### **Get Order Details**
```json
GET /api/v1/orders/{{order_id}}
Authorization: Bearer {{access_token}}
```

#### **Modify Order**
```json
PUT /api/v1/orders/{{order_id}}
Authorization: Bearer {{access_token}}
{
  "price": 1.0860,
  "stop_loss": 1.0810,
  "take_profit": 1.0910
}
```

#### **Cancel Order**
```json
DELETE /api/v1/orders/{{order_id}}
Authorization: Bearer {{access_token}}
```

### **Step 9: Trade History**

#### **Get Trades**
```json
GET /api/v1/trades/?account_id={{account_id}}&limit=100
Authorization: Bearer {{access_token}}
```

#### **Get Trade Statistics**
```json
GET /api/v1/trades/statistics?account_id={{account_id}}
Authorization: Bearer {{access_token}}
```

### **Step 10: Account Management**

#### **Get Account Details**
```json
GET /api/v1/accounts/{{account_id}}
Authorization: Bearer {{access_token}}
```

#### **Update Account**
```json
PUT /api/v1/accounts/{{account_id}}
Authorization: Bearer {{access_token}}
{
  "account_name": "Updated Account Name",
  "risk_level": "high"
}
```

---

## 🔐 **Authentication Flow**

### **Complete Authentication Workflow:**

1. **Register** → Get user ID
2. **Send Verification Code** → Get 6-digit code
3. **Verify Email** → Mark user as verified
4. **Login** → Get access & refresh tokens
5. **Use Access Token** → For all protected endpoints

### **Token Management:**
- **Access Token**: Valid for 30 minutes
- **Refresh Token**: Valid for 7 days
- **Auto-refresh**: Use refresh endpoint when access token expires

---

## 📊 **Testing Scenarios**

### **Scenario 1: Complete Trading Flow**
1. Register user
2. Verify email
3. Login
4. Create demo account
5. Get market data
6. Place market order
7. Monitor order status
8. View trade history

### **Scenario 2: Order Management**
1. Login with existing user
2. Create account
3. Place limit order
4. Modify order
5. Cancel order
6. Check order history

### **Scenario 3: Account Management**
1. Login
2. Create multiple accounts
3. Update account settings
4. View account details
5. Delete account

### **Scenario 4: Password Reset**
1. Use existing user
2. Request password reset
3. Verify reset code
4. Set new password
5. Login with new password

---

## 🚨 **Common Issues & Solutions**

### **Issue 1: 401 Unauthorized**
**Solution**: Check if access token is valid and properly set in environment

### **Issue 2: 403 Forbidden**
**Solution**: Ensure user email is verified before accessing protected endpoints

### **Issue 3: 422 Validation Error**
**Solution**: Check request body format and required fields

### **Issue 4: 404 Not Found**
**Solution**: Verify endpoint URL and account/order IDs

---

## 📈 **Performance Testing**

### **Load Testing Scenarios:**
1. **Concurrent Users**: Test with multiple users
2. **Rapid Orders**: Place multiple orders quickly
3. **Large Data**: Request large datasets
4. **WebSocket**: Test real-time connections

### **Monitoring Points:**
- Response times
- Error rates
- Token expiration
- Database performance

---

## 🔧 **Environment Variables**

### **Required Variables:**
- `base_url`: API base URL
- `access_token`: JWT access token
- `account_id`: Trading account ID
- `order_id`: Order ID for modifications

### **Test Data Variables:**
- `test_email`: Test user email
- `test_password`: Test user password
- `symbol`: Trading symbol (EURUSD)
- `quantity`: Order quantity

---

## 📚 **Additional Resources**

### **API Documentation:**
- **Swagger UI**: `{{base_url}}/api/docs`
- **ReDoc**: `{{base_url}}/api/redoc`
- **OpenAPI JSON**: `{{base_url}}/api/openapi.json`

### **WebSocket Testing:**
- **Connection**: `ws://{{base_url}}/ws`
- **Authentication**: Send JWT token in connection
- **Real-time Updates**: Market prices, order status

---

## ✅ **Testing Checklist**

- [ ] User registration works
- [ ] Email verification works
- [ ] Login returns tokens
- [ ] Account creation works
- [ ] Market data accessible
- [ ] Orders can be placed
- [ ] Order management works
- [ ] Trade history accessible
- [ ] Error handling works
- [ ] Authentication required for protected endpoints

---

## 🎉 **Ready for Production!**

Once all tests pass, your EdgeTrade API is ready for production use. The Postman collection provides comprehensive testing coverage for all API endpoints and workflows.

**Next Steps:**
1. Run through all test scenarios
2. Verify error handling
3. Test with real data
4. Monitor performance
5. Deploy to production
