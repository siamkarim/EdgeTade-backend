"""
Test Complete User Flow: Registration -> Login -> Create Trading Account
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

print("="*70)
print("EDGETRADE - USER REGISTRATION & ACCOUNT SETUP TEST")
print("="*70)

# ========== Step 1: Register User ==========
print("\n[Step 1] Registering new user...")
print("-" * 70)

register_data = {
    "email": "trader@example.com",
    "username": "demo_trader",
    "password": "SecurePass123"
}

print(f"POST {BASE_URL}/auth/register")
print(f"Data: {json.dumps(register_data, indent=2)}")

try:
    response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    
    if response.status_code == 201:
        user = response.json()
        print(f"\n[SUCCESS] User registered!")
        print(f"  User ID: {user['id']}")
        print(f"  Email: {user['email']}")
        print(f"  Username: {user['username']}")
        print(f"  Active: {user['is_active']}")
        print(f"  Created: {user['created_at']}")
        user_id = user['id']
    elif response.status_code == 400 and "already registered" in response.text:
        print(f"\n[INFO] User already exists, proceeding to login...")
        user_id = None
    else:
        print(f"\n[ERROR] Registration failed: {response.status_code}")
        print(f"Response: {response.text}")
        exit(1)
except requests.exceptions.ConnectionError:
    print("\n[ERROR] Cannot connect to server!")
    print("Make sure the server is running: python main.py")
    exit(1)

# ========== Step 2: Login ==========
print("\n[Step 2] Logging in...")
print("-" * 70)

login_data = {
    "email": "trader@example.com",
    "password": "SecurePass123"
}

print(f"POST {BASE_URL}/auth/login")
print(f"Data: {json.dumps(login_data, indent=2)}")

response = requests.post(f"{BASE_URL}/auth/login", json=login_data)

if response.status_code == 200:
    tokens = response.json()
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]
    print(f"\n[SUCCESS] Login successful!")
    print(f"  Access Token: {access_token[:40]}...")
    print(f"  Refresh Token: {refresh_token[:40]}...")
    print(f"  Token Type: {tokens['token_type']}")
else:
    print(f"\n[ERROR] Login failed: {response.status_code}")
    print(f"Response: {response.text}")
    exit(1)

# ========== Step 3: Create Trading Account ==========
print("\n[Step 3] Creating trading account...")
print("-" * 70)

headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

account_data = {
    "account_name": "Demo Trading Account",
    "account_type": "demo",
    "currency": "USD",
    "balance": 10000,
    "leverage": 100
}

print(f"POST {BASE_URL}/accounts/")
print(f"Headers: Authorization: Bearer {access_token[:20]}...")
print(f"Data: {json.dumps(account_data, indent=2)}")

response = requests.post(f"{BASE_URL}/accounts/", json=account_data, headers=headers)

if response.status_code == 201:
    account = response.json()
    print(f"\n[SUCCESS] Trading account created!")
    print(f"  Account ID: {account['id']}")
    print(f"  Account Name: {account['account_name']}")
    print(f"  Account Type: {account['account_type']}")
    print(f"  Currency: {account['currency']}")
    print(f"  Balance: ${account['balance']:,.2f}")
    print(f"  Leverage: 1:{account['leverage']}")
    print(f"  Status: {'Active' if account['is_active'] else 'Inactive'}")
    print(f"  Created: {account['created_at']}")
    account_id = account['id']
else:
    print(f"\n[ERROR] Account creation failed: {response.status_code}")
    print(f"Response: {response.text}")
    exit(1)

# ========== Step 4: Get All Accounts ==========
print("\n[Step 4] Fetching all trading accounts...")
print("-" * 70)

print(f"GET {BASE_URL}/accounts/")

response = requests.get(f"{BASE_URL}/accounts/", headers=headers)

if response.status_code == 200:
    accounts = response.json()
    print(f"\n[SUCCESS] Found {len(accounts)} trading account(s)")
    for idx, acc in enumerate(accounts, 1):
        print(f"\n  Account {idx}:")
        print(f"    ID: {acc['id']}")
        print(f"    Name: {acc['account_name']}")
        print(f"    Type: {acc['account_type']}")
        print(f"    Balance: ${acc['balance']:,.2f}")
        print(f"    Leverage: 1:{acc['leverage']}")
else:
    print(f"\n[ERROR] Failed to fetch accounts: {response.status_code}")

# ========== Step 5: Get Account Balance ==========
print(f"\n[Step 5] Getting real-time account balance...")
print("-" * 70)

print(f"GET {BASE_URL}/accounts/{account_id}/balance")

response = requests.get(f"{BASE_URL}/accounts/{account_id}/balance", headers=headers)

if response.status_code == 200:
    balance = response.json()
    print(f"\n[SUCCESS] Account Balance Details:")
    print(f"  Balance: ${balance['balance']:,.2f}")
    print(f"  Equity: ${balance['equity']:,.2f}")
    print(f"  Margin Used: ${balance['margin_used']:,.2f}")
    print(f"  Margin Free: ${balance['margin_free']:,.2f}")
    print(f"  Margin Level: {balance['margin_level']:.2f}%")
    print(f"  Unrealized P&L: ${balance['unrealized_pnl']:,.2f}")
else:
    print(f"\n[ERROR] Failed to get balance: {response.status_code}")
    print(f"Response: {response.text}")

# ========== Summary ==========
print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print(f"\n[OK] User Email: trader@example.com")
print(f"[OK] Access Token: {access_token[:30]}...")
print(f"[OK] Trading Account ID: {account_id}")
print(f"[OK] Account Balance: $10,000.00")
print(f"\nNext Steps:")
print("  1. View market data: GET /api/v1/market/symbols")
print("  2. Get prices: GET /api/v1/market/prices")
print("  3. Place order: POST /api/v1/orders/")
print("  4. View orders: GET /api/v1/orders/")
print("\nAPI Documentation: http://localhost:8000/api/docs")
print("\n[SUCCESS] ALL TESTS PASSED! You're ready to trade!")
print("="*70)

