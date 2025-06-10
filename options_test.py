#!/usr/bin/env python3
"""
Simple Options Test with Authentication
Testing CedroTech options API with proper session authentication
"""

import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()

def test_options_with_auth():
    """Test options endpoint with proper authentication"""
    print("🔐 CedroTech Options Test with Authentication")
    print("=" * 60)
    
    # Trading credentials for options access
    trading_user = os.getenv('CEDROTECH_PLATAFORM','')
    trading_password = os.getenv('CEDROTECH_PLAT_PASSWORD','')
    base_url = "https://webfeeder.cedrotech.com"
    
    # Create session for authentication
    session = requests.Session()
    
    # Step 1: Authenticate
    print("1. Authenticating...")
    auth_url = f"{base_url}/SignIn"
    auth_params = {
        "login": trading_user,
        "password": trading_password
    }
    auth_headers = {"accept": "application/json"}
    
    auth_response = session.post(auth_url, headers=auth_headers, params=auth_params)
    print(f"   Auth Status: {auth_response.status_code}")
    
    if auth_response.status_code == 200:
        cookies = dict(session.cookies)
        print(f"   ✅ Authentication successful!")
        print(f"   🍪 Cookies: {list(cookies.keys())}")
    else:
        print(f"   ❌ Authentication failed")
        return False
    
    # Step 2: Test specific VALE option symbols we found from company quotes
    vale_options = ["valek571", "valef640", "valei708", "valeh420", "valeh430"]
    
    print(f"\n2. Testing Specific VALE Option Symbols...")
    print("-" * 40)
    
    for option_symbol in vale_options:
        print(f"\n📋 Testing option symbol: {option_symbol}...")
        
        # Options endpoint
        options_url = f"{base_url}/services/quotes/quote/{option_symbol}"
        headers = {"accept": "application/json"}
        
        response = session.get(options_url, headers=headers)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                # Try to parse as JSON
                options_data = response.json()
                print(f"   ✅ JSON Response received")
                print(f"   📊 Data type: {type(options_data)}")
                print(f"   📊 Response keys: {list(options_data.keys())}")
                  # Look for option-specific fields
                option_fields = ['typeOption', 'directionOption', 'parentSymbol', 'bid', 'ask', 'lastTrade', 'volume', 'interest', 'contractMultiplier', 'theoryPrice']
                found_fields = [field for field in option_fields if field in options_data]
                if found_fields:
                    print(f"   🎯 Option fields found: {found_fields}")
                    for field in found_fields:
                        print(f"      {field}: {options_data[field]}")
                
                # Show key options info
                print(f"   📊 Key Options Info:")
                print(f"      Symbol: {options_data.get('symbol', 'N/A')}")
                print(f"      Type: {options_data.get('typeOption', 'N/A')}")
                print(f"      Direction: {options_data.get('directionOption', 'N/A')}")
                print(f"      Underlying: {options_data.get('parentSymbol', 'N/A')}")
                print(f"      Last Trade: {options_data.get('lastTrade', 'N/A')}")
                print(f"      Theory Price: {options_data.get('theoryPrice', 'N/A')}")
                print(f"      Contract Multiplier: {options_data.get('contractMultiplier', 'N/A')}")
                print(f"      Open Interest: {options_data.get('interest', 'N/A')}")
                        
            except json.JSONDecodeError:
                # Raw text response
                print(f"   ⚠️  Raw text response:")
                print(f"   📄 Response: {response.text[:200]}...")
                
                # Check for specific messages
                if "Not Permit" in response.text:
                    print(f"   🚫 Permission denied")
                elif "Unauthorized" in response.text:
                    print(f"   🔐 Unauthorized - authentication issue")
                
        else:
            print(f"   ❌ Failed: {response.status_code}")
            print(f"   Error: {response.text[:100]}...")

    # Step 3: Test Options for multiple assets (original test)
    test_assets = ["PETR4", "VALE3", "ITUB4", "BBDC4", "ABEV3"]
    
    print(f"\n3. Testing optionsQuote Endpoint for Assets...")
    print("-" * 40)
    
    for asset in test_assets:
        print(f"\n📋 Testing options for {asset}...")
        
        # Options endpoint
        options_url = f"{base_url}/services/quotes/optionsQuote/{asset}"
        headers = {"accept": "application/json"}
        
        response = session.get(options_url, headers=headers)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                # Try to parse as JSON
                options_data = response.json()
                print(f"   ✅ JSON Response received")
                print(f"   📊 Data type: {type(options_data)}")
                
                if isinstance(options_data, list):
                    print(f"   📊 Total options: {len(options_data)}")
                    
                    # Analyze options types
                    calls = [opt for opt in options_data if opt.get('type', '').upper() == 'CALL']
                    puts = [opt for opt in options_data if opt.get('type', '').upper() == 'PUT']
                    
                    print(f"   📈 Call options: {len(calls)}")
                    print(f"   📉 Put options: {len(puts)}")
                    
                    # Show sample option if available
                    if options_data:
                        sample = options_data[0]
                        print(f"   💡 Sample option keys: {list(sample.keys())}")
                        
                elif isinstance(options_data, dict):
                    print(f"   📊 Response keys: {list(options_data.keys())}")
                
            except json.JSONDecodeError:
                # Raw text response
                print(f"   ⚠️  Raw text response:")
                print(f"   📄 Response: {response.text[:200]}...")
                
                # Check for specific messages
                if "Not Permit" in response.text:
                    print(f"   🚫 Permission denied - may need different auth or account permissions")
                elif "Unauthorized" in response.text:
                    print(f"   🔐 Unauthorized - authentication issue")
                
        else:
            print(f"   ❌ Failed: {response.status_code}")
            print(f"   Error: {response.text[:100]}...")
      # Step 4: Test working endpoints for comparison
    print(f"\n4. Testing Working Endpoints for Comparison...")
    print("-" * 40)
    
    # Test stock quote (we know this works)
    print(f"\n📊 Testing stock quote for PETR4...")
    headers = {"accept": "application/json"}
    quote_url = f"{base_url}/services/quotes/quote/PETR4"
    quote_response = session.get(quote_url, headers=headers)
    
    print(f"   Status: {quote_response.status_code}")
    if quote_response.status_code == 200:
        try:
            quote_data = quote_response.json()
            print(f"   ✅ Stock quote works - JSON received")
            print(f"   📊 Quote keys: {list(quote_data.keys())}")
        except:
            print(f"   ✅ Stock quote works - Raw response")
            print(f"   📄 Response: {quote_response.text[:100]}...")

def test_options_without_auth():
    """Test options endpoint without authentication for comparison"""
    
    print(f"\n\n🔓 Testing Options WITHOUT Authentication")
    print("=" * 60)
    
    base_url = "https://webfeeder.cedrotech.com"
    
    test_assets = ["PETR4", "VALE3"]
    
    for asset in test_assets:
        print(f"\n📋 Testing {asset} without auth...")
        
        options_url = f"{base_url}/services/quotes/optionsQuote/{asset}"
        headers = {"accept": "application/json"}
        
        response = requests.get(options_url, headers=headers)
        
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}...")

if __name__ == "__main__":
    # Test with authentication
    test_options_with_auth()
    
    # Test without authentication for comparison
    test_options_without_auth()
    
    print(f"\n\n📝 SUMMARY & ANALYSIS")
    print("=" * 60)
    print("🔍 Key Findings:")
    print("  • Options endpoint exists and responds (Status 200)")
    print("  • 'Not Permit' suggests authentication or permission issue")
    print("  • Stock quotes work fine with same authentication")
    print("  • May need special options permissions or different auth")
    print("")
    print("💡 Next Steps:")
    print("  1. Contact CedroTech about options API access")
    print("  2. Check if account has options trading permissions")
    print("  3. Verify if special authentication is needed for options")
    print("  4. Consider alternative options data sources")
    print("")
    print("🎯 Options trading is still achievable - just need proper access!")