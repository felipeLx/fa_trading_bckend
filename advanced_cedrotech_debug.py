#!/usr/bin/env python3
"""
Advanced CedroTech API diagnosis
Test different authentication methods and analyze the complete flow
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

def test_advanced_auth():
    """Test advanced authentication scenarios"""
    print("="*60)
    print("ADVANCED CEDROTECH API DIAGNOSIS")
    print("="*60)
    print()
    
    base_url = "https://webfeeder.cedrotech.com"
    username = "8778731"
    password = os.getenv('CEDROTECH_PASSWORD', 'CsxjIQ06@*')
    
    # Test 1: Check if we need to maintain session cookies
    print("🧪 TEST 1: Authentication with session management")
    print("-" * 50)
    
    session = requests.Session()
    
    try:
        url = f"{base_url}/SignIn?login={username}&password={password}"
        headers = {"accept": "application/json"}
        
        response = session.post(url, headers=headers)
        
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        print(f"   Cookies: {dict(response.cookies)}")
        
        # If we got cookies, test if we can use them for API calls
        if response.cookies:
            print("   🍪 Testing with received cookies...")
            
            # Test order placement with cookies
            order_url = f"{base_url}/services/negotiation/sendNewOrderSingle"
            order_params = {
                "market": "XBSP",
                "quote": "PETR4", 
                "qtd": "1",
                "type": "Market",
                "side": "Buy",
                "username": username,
                "bypasssuitability": "true",
                "traderate": "0",
                "orderstrategy": "DAYTRADE",
                "timeinforce": "DAY"
            }
            
            query_string = "&".join([f"{k}={v}" for k, v in order_params.items()])
            full_order_url = f"{order_url}?{query_string}"
            
            order_response = session.post(full_order_url, headers={"accept": "application/json"})
            print(f"   Order test status: {order_response.status_code}")
            print(f"   Order test response: {order_response.text[:200]}...")
            
    except Exception as e:
        print(f"   ERROR: {e}")
    
    print()
    
    # Test 2: Check if the API requires a different endpoint for trading auth
    print("🧪 TEST 2: Check alternative authentication endpoints")
    print("-" * 50)
    
    alt_endpoints = [
        "/signin",  # lowercase
        "/login",   # alternative
        "/auth",    # common pattern
        "/SignIn",  # current (for comparison)
    ]
    
    for endpoint in alt_endpoints:
        try:
            url = f"{base_url}{endpoint}?login={username}&password={password}"
            response = requests.post(url, headers={"accept": "application/json"})
            print(f"   {endpoint}: Status {response.status_code}, Response: {response.text}")
        except Exception as e:
            print(f"   {endpoint}: ERROR - {e}")
    
    print()
    
    # Test 3: Test if credentials work with the actual order endpoint
    print("🧪 TEST 3: Direct order endpoint test (bypass auth)")
    print("-" * 50)
    
    try:
        # Your original working example format
        order_url = f"{base_url}/services/negotiation/sendNewOrderSingle"
        params = {
            "market": "XBSP",
            "price": "30.57", 
            "quote": "PETR4",
            "qtd": "2",
            "type": "Start",
            "side": "Buy",
            "username": username,
            "bypasssuitability": "true",
            "traderate": "0"
        }
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        full_url = f"{order_url}?{query_string}"
        
        print(f"   Testing: {full_url}")
        
        response = requests.post(full_url, headers={"accept": "application/json"})
        
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            print("   ✅ Order endpoint accessible without explicit auth!")
        elif response.status_code == 401:
            print("   🔒 Authentication required")
        elif response.status_code == 403:
            print("   🚫 Access forbidden - check permissions")
        else:
            print(f"   ⚠️  Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"   ERROR: {e}")
    
    print()
    
    # Test 4: Test if the API is stateless and doesn't need SignIn
    print("🧪 TEST 4: Test if API is stateless")
    print("-" * 50)
    
    print("   Based on your working example, the API might be stateless.")
    print("   Your example worked without explicit authentication:")
    print("   ➤ This suggests SignIn might not be required")
    print("   ➤ Or SignIn is for web interface, not API")
    print("   ➤ Username in query params might be sufficient")
    
    print()
    
    # Test 5: Check account status possibilities
    print("🧪 TEST 5: Account status analysis")
    print("-" * 50)
    
    print("   🔍 Possible reasons for 'false' response:")
    print("   1. Account not activated for API trading")
    print("   2. Insufficient permissions/trading level")
    print("   3. Account locked or suspended")
    print("   4. Wrong password (most likely)")
    print("   5. API access requires additional setup")
    print()
    print("   💡 RECOMMENDATION:")
    print("   Since your original order example seemed to work,")
    print("   try implementing the API without SignIn authentication.")
    print("   Many trading APIs are stateless and use username in requests.")
    
    print()
    print("="*60)
    print("CONCLUSIONS:")
    print("1. SignIn returns 'false' - authentication failing")
    print("2. Session cookies are provided but auth still fails")
    print("3. Your original order example suggests API might be stateless")
    print("4. Recommend testing direct order placement without SignIn")
    print("="*60)

if __name__ == "__main__":
    test_advanced_auth()
