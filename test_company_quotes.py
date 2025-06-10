#!/usr/bin/env python3
"""
Test Company Quotes Endpoint
Testing CedroTech company quotes API to get assets by company including options
"""

import requests
import json

def test_company_quotes():
    """Test company quotes endpoint with different asset types"""
    
    print("🏢 CedroTech Company Quotes Test")
    print("=" * 60)
      # Trading credentials
    trading_user = "btg8778731"
    trading_password = "867790"
    base_url = "https://webfeeder.cedrotech.com"
    
    # Create session for authentication
    session = requests.Session()
    
    # Step 1: Authenticate
    print("1. Authenticating with trading credentials...")
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
    
    # Step 2: Test Company Quotes for different companies and asset types
    print(f"\n2. Testing Company Quotes...")
    print("-" * 40)
    
    # Test parameters
    test_companies = ["PETROBRAS", "VALE", "ITAU", "BRADESCO"]
    
    # Asset types according to documentation:
    # 1 = à vista (spot/stock)
    # 2 = opções (options) 
    # 3 = índice (index)
    # 7 = Forex
    # 10 = NYSE
    asset_types = {
        "1": "Stocks (à vista)",
        "2": "Options (opções)", 
        "3": "Index (índice)",
        "7": "Forex",
        "10": "NYSE"
    }
    
    # Market IDs:
    # 1 = Bovespa
    # 3 = BMF  
    # 6 = Soma
    markets = {
        "1": "Bovespa",
        "3": "BMF",
        "6": "Soma"
    }
    
    headers = {"accept": "application/json"}
    
    for company in test_companies:
        print(f"\n🏢 Testing company: {company}")
        print("-" * 30)
        
        # Test different asset types for this company
        for type_id, type_name in asset_types.items():
            print(f"\n  📊 Type {type_id}: {type_name}")
            
            # Test different markets
            for market_id, market_name in markets.items():
                
                # Company quotes endpoint
                company_url = f"{base_url}/services/quotes/companyQuotes"
                params = {
                    "company": company,
                    "types": type_id,
                    "markets": market_id
                }
                
                response = session.get(company_url, headers=headers, params=params)
                
                print(f"    Market {market_id} ({market_name}): Status {response.status_code}", end="")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if isinstance(data, list):
                            print(f" - {len(data)} assets found")
                              # Show sample if options found
                            if type_id == "2" and data:  # Options
                                print(f"      🎯 OPTIONS FOUND! Sample:")
                                sample = data[0]
                                
                                # Handle different data types
                                if isinstance(sample, dict):
                                    print(f"      📋 Keys: {list(sample.keys())}")
                                    if 'symbol' in sample:
                                        print(f"      🔖 Symbol: {sample['symbol']}")
                                    if 'name' in sample:
                                        print(f"      📝 Name: {sample['name']}")
                                elif isinstance(sample, str):
                                    print(f"      🔖 Sample symbol: {sample}")
                                    # Show first few symbols
                                    symbols = data[:5] if len(data) >= 5 else data
                                    print(f"      📋 First symbols: {symbols}")
                                else:
                                    print(f"      📊 Sample type: {type(sample)}")
                                    print(f"      📄 Sample: {sample}")
                        
                        elif isinstance(data, dict):
                            print(f" - Dict response")
                            print(f"      📋 Keys: {list(data.keys())}")
                        
                        else:
                            print(f" - {type(data)} response")
                            
                    except json.JSONDecodeError:
                        print(f" - Raw text: {response.text[:50]}...")
                        
                        # Check for permission issues
                        if "Not Permit" in response.text:
                            print(f"      🚫 Permission denied")
                        elif "Unauthorized" in response.text:
                            print(f"      🔐 Unauthorized")
                else:
                    print(f" - Error: {response.text[:50]}...")

def test_company_quotes_without_auth():
    """Test company quotes endpoint without authentication"""
    
    print(f"\n\n🔓 Testing Company Quotes WITHOUT Authentication")
    print("=" * 60)
    
    base_url = "https://webfeeder.cedrotech.com"
    
    # Test one company with options
    company = "PETROBRAS"
    type_id = "2"  # Options
    market_id = "1"  # Bovespa
    
    print(f"\n📋 Testing {company} options without auth...")
    
    company_url = f"{base_url}/services/quotes/companyQuotes"
    params = {
        "company": company,
        "types": type_id,
        "markets": market_id
    }
    headers = {"accept": "application/json"}
    
    response = requests.get(company_url, headers=headers, params=params)
    
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text[:200]}...")

if __name__ == "__main__":
    # Test with authentication
    test_company_quotes()
    
    # Test without authentication for comparison
    test_company_quotes_without_auth()
    
    print(f"\n\n📝 COMPANY QUOTES TEST SUMMARY")
    print("=" * 60)
    print("🔍 What we're testing:")
    print("  • Company quotes endpoint: /services/quotes/companyQuotes")
    print("  • Asset types: 1(stocks), 2(options), 3(index), 7(forex), 10(NYSE)")
    print("  • Markets: 1(Bovespa), 3(BMF), 6(Soma)")
    print("  • Companies: PETROBRAS, VALE, ITAU, BRADESCO")
    print("")
    print("🎯 Goal:")
    print("  • Find alternative way to access options data")
    print("  • Test if company-based options access works")
    print("  • Identify which markets/companies have options")
    print("")
    print("💡 This could be the key to options integration!")
