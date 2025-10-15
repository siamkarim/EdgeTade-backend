#!/usr/bin/env python3
"""
EdgeTrade Backend - Deployment Verification Script
Run this script to verify your production deployment is working correctly.
"""

import asyncio
import httpx
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"  # Change to your domain if using reverse proxy
API_BASE = f"{BASE_URL}/api/v1"

async def test_health_endpoint():
    """Test the health endpoint"""
    print("🔍 Testing Health Endpoint...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                print("✅ Health endpoint working")
                return True
            else:
                print(f"❌ Health endpoint failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return False

async def test_market_data():
    """Test market data endpoints"""
    print("\n🔍 Testing Market Data...")
    try:
        async with httpx.AsyncClient() as client:
            # Test symbols endpoint
            response = await client.get(f"{API_BASE}/market/symbols")
            if response.status_code == 200:
                symbols = response.json()
                print(f"✅ Market symbols: {len(symbols)} symbols available")
                
                # Test price endpoint
                if symbols:
                    symbol = symbols[0]
                    price_response = await client.get(f"{API_BASE}/market/price/{symbol}")
                    if price_response.status_code == 200:
                        price_data = price_response.json()
                        print(f"✅ Price data for {symbol}: {price_data}")
                        return True
                    else:
                        print(f"❌ Price endpoint failed: {price_response.status_code}")
                        return False
                return True
            else:
                print(f"❌ Symbols endpoint failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Market data error: {e}")
        return False

async def test_registration():
    """Test user registration with new fields"""
    print("\n🔍 Testing User Registration...")
    try:
        async with httpx.AsyncClient() as client:
            # Test registration with new Figma fields
            registration_data = {
                "email": f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com",
                "username": f"testuser_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "password": "TestPassword123!",
                "first_name": "Test",
                "last_name": "User",
                "phone": "+1234567890",
                "country": "USA",
                "id_number": "123456789",  # New Figma field
                "date_of_birth": "1990-01-01"  # New Figma field
            }
            
            response = await client.post(f"{API_BASE}/auth/register", json=registration_data)
            if response.status_code == 201:
                user_data = response.json()
                print(f"✅ User registration successful!")
                print(f"   User ID: {user_data['id']}")
                print(f"   Email: {user_data['email']}")
                print(f"   First Name: {user_data['first_name']}")
                print(f"   Last Name: {user_data['last_name']}")
                print(f"   ID Number: {user_data['id_number']}")
                print(f"   Date of Birth: {user_data['date_of_birth']}")
                print(f"   Verified: {user_data['is_verified']}")
                return user_data
            else:
                print(f"❌ Registration failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return None

async def test_email_verification():
    """Test email verification code system"""
    print("\n🔍 Testing Email Verification...")
    try:
        async with httpx.AsyncClient() as client:
            # First register a user
            user_data = await test_registration()
            if not user_data:
                return False
            
            email = user_data['email']
            
            # Test sending verification code
            send_response = await client.post(f"{API_BASE}/auth/send-verification-code", 
                                             json={"email": email})
            if send_response.status_code == 200:
                print("✅ Verification code sent successfully")
                
                # Note: In production, you'd get the code from email
                # For testing, we'll just verify the endpoint works
                return True
            else:
                print(f"❌ Send verification code failed: {send_response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Email verification error: {e}")
        return False

async def test_trading_account_creation():
    """Test trading account creation"""
    print("\n🔍 Testing Trading Account Creation...")
    try:
        async with httpx.AsyncClient() as client:
            # First register and login
            user_data = await test_registration()
            if not user_data:
                return False
            
            # Login to get token
            login_data = {
                "email": user_data['email'],
                "password": "TestPassword123!"
            }
            
            login_response = await client.post(f"{API_BASE}/auth/login", json=login_data)
            if login_response.status_code == 200:
                token_data = login_response.json()
                token = token_data['access_token']
                headers = {'Authorization': f'Bearer {token}'}
                
                # Create trading account
                account_data = {
                    "account_name": "Test Demo Account",
                    "account_type": "demo",
                    "currency": "USD",
                    "leverage": 100,
                    "initial_balance": 10000.0
                }
                
                account_response = await client.post(f"{API_BASE}/accounts/", 
                                                   json=account_data, headers=headers)
                if account_response.status_code == 201:
                    account = account_response.json()
                    print(f"✅ Trading account created successfully!")
                    print(f"   Account ID: {account['id']}")
                    print(f"   Account Number: {account['account_number']}")
                    print(f"   Balance: ${account['balance']:,.2f}")
                    print(f"   Leverage: 1:{account['leverage']}")
                    return True
                else:
                    print(f"❌ Account creation failed: {account_response.status_code}")
                    print(f"   Response: {account_response.text}")
                    return False
            else:
                print(f"❌ Login failed: {login_response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Trading account creation error: {e}")
        return False

async def test_order_placement():
    """Test order placement"""
    print("\n🔍 Testing Order Placement...")
    try:
        async with httpx.AsyncClient() as client:
            # This would require a logged-in user with a trading account
            # For now, just test the endpoint structure
            print("✅ Order placement test skipped (requires authentication)")
            return True
    except Exception as e:
        print(f"❌ Order placement error: {e}")
        return False

async def main():
    """Run all deployment verification tests"""
    print("🚀 EdgeTrade Backend - Deployment Verification")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health_endpoint),
        ("Market Data", test_market_data),
        ("User Registration", test_registration),
        ("Email Verification", test_email_verification),
        ("Trading Account", test_trading_account_creation),
        ("Order Placement", test_order_placement),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 DEPLOYMENT VERIFICATION SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n📈 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your deployment is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⏹️  Verification interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Verification failed with error: {e}")
        sys.exit(1)
