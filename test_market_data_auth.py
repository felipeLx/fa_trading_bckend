#!/usr/bin/env python3
"""
Test CedroTech Market Data Authentication
Using platform credentials to access market data API
"""

import requests
import json
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()

def test_market_data_authentication():
    """
    Test authentication for CedroTech Market Data API using platform credentials
    Returns session object for subsequent API calls
    """
    print("🔐 TESTING CEDROTECH MARKET DATA AUTHENTICATION")
    print("=" * 60)
    
    # Platform credentials
    platform_user = os.getenv('CEDROTECH_PLATAFORM','')
    platform_password = os.getenv('CEDROTECH_PLAT_PASSWORD', '')
    
    print(f"👤 Platform User: {platform_user}")
    print(f"🔑 Password: {'*' * len(platform_password)}")
    print()
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    try:
        # Authentication endpoint from documentation
        auth_url = "https://webfeeder.cedrotech.com/SignIn"
        
        # Query parameters as specified in documentation
        params = {
            "login": platform_user,
            "password": platform_password
        }
        
        headers = {
            "accept": "application/json"
        }
        
        print(f"📡 Making authentication request...")
        print(f"   URL: {auth_url}")
        print(f"   Method: POST")
        print(f"   Headers: {headers}")
        print(f"   Params: login={platform_user}, password=***")
        print()
        
        # Make authentication request using session
        response = session.post(auth_url, headers=headers, params=params)
        
        print(f"📊 Authentication Response:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Headers: {dict(response.headers)}")
        print(f"   Cookies Received: {dict(session.cookies)}")
        print()
        
        if response.status_code == 200:
            try:
                auth_result = response.json()
                print(f"✅ AUTHENTICATION SUCCESSFUL!")
                print(f"   Response JSON:")
                print(json.dumps(auth_result, indent=2, ensure_ascii=False))
                
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "auth_data": auth_result,
                    "platform_user": platform_user,
                    "session": session
                }
                
            except json.JSONDecodeError:
                print(f"✅ AUTHENTICATION SUCCESSFUL (Non-JSON Response)")
                print(f"   Raw Response: {response.text}")
                
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "raw_response": response.text,
                    "platform_user": platform_user,
                    "session": session
                }
                
        elif response.status_code == 401:
            print(f"❌ AUTHENTICATION FAILED")
            print(f"   Invalid credentials or account not authorized for market data")
            print(f"   Response: {response.text}")
            
            return {
                "success": False,
                "status_code": response.status_code,
                "error": "Invalid credentials",
                "raw_response": response.text,
                "session": None
            }
            
        elif response.status_code == 403:
            print(f"❌ ACCESS FORBIDDEN")
            print(f"   Account may not have market data permissions")
            print(f"   Response: {response.text}")
            
            return {
                "success": False,
                "status_code": response.status_code,
                "error": "Access forbidden",
                "raw_response": response.text,
                "session": None
            }
            
        else:
            print(f"⚠️ UNEXPECTED RESPONSE")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            
            return {
                "success": False,
                "status_code": response.status_code,
                "error": f"HTTP {response.status_code}",
                "raw_response": response.text,
                "session": None
            }
            
    except Exception as e:
        print(f"💥 EXCEPTION OCCURRED")
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            "success": False,
            "error": str(e),
            "session": None
        }

def test_market_data_endpoints(auth_result, session):
    """
    Test market data endpoints after successful authentication using session cookies
    """
    if not auth_result.get("success"):
        print(f"\n❌ Cannot test market data - authentication failed")
        return
    
    print(f"\n📈 TESTING MARKET DATA ENDPOINTS")
    print("=" * 60)
    
    # Common test endpoints for market data
    test_endpoints = [
        {
            "name": "Stock Quote - PETR4",
            "url": "https://webfeeder.cedrotech.com/services/quotes/Quote/PETR4",
            "method": "GET"
        },
        {
            "name": "Stock Quote - VALE3", 
            "url": "https://webfeeder.cedrotech.com/services/quotes/Quote/VALE3",
            "method": "GET"
        },
        {
            "name": "Market List",
            "url": "https://webfeeder.cedrotech.com/services/quotes/Markets",
            "method": "GET"
        }
    ]
    
    headers = {"accept": "application/json"}
    
    print(f"🔑 Using session cookies from authentication")
    print(f"   Cookies: {dict(session.cookies)}")
    print()
    
    for endpoint in test_endpoints:
        try:
            print(f"🧪 Testing: {endpoint['name']}")
            print(f"   URL: {endpoint['url']}")
            
            # Use the same session that was authenticated
            response = session.get(endpoint['url'], headers=headers)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✅ SUCCESS - Data received")
                    print(f"   Sample: {str(data)[:200]}...")
                    
                    # Pretty print the data structure
                    if isinstance(data, dict):
                        print(f"   📊 Data structure:")
                        for key, value in list(data.items())[:5]:  # Show first 5 keys
                            print(f"      {key}: {str(value)[:50]}...")
                    
                except:
                    print(f"   ✅ SUCCESS - Non-JSON response")
                    print(f"   Response: {response.text[:200]}...")
            else:
                print(f"   ❌ FAILED - {response.status_code}")
                print(f"   Error: {response.text[:100]}...")
            
            print()
            
        except Exception as e:
            print(f"   💥 ERROR: {e}")
            print()

if __name__ == "__main__":
    print("🧪 CEDROTECH MARKET DATA API TEST")
    print("=" * 60)
    print("Testing authentication and market data access with platform credentials")
    print()
    
    # Test authentication
    auth_result = test_market_data_authentication()
    
    # Test market data endpoints if auth successful
    if auth_result.get("success") and auth_result.get("session"):
        test_market_data_endpoints(auth_result, auth_result["session"])
    
    print(f"\n📝 SUMMARY:")
    print("=" * 60)
    if auth_result.get("success"):
        print("✅ Market data authentication working!")
        print("🎯 You can now access CedroTech market data APIs")
        print("💡 This is different from trading APIs - market data is read-only")
    else:
        print("❌ Market data authentication failed")
        print("🔧 Check credentials or contact CedroTech support")
    
    print(f"\n🎯 NEXT STEPS:")
    print("If authentication works, we can integrate market data into your trading robot!")
    print("This will give you real-time prices for better trading decisions.")
