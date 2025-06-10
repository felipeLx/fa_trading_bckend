#!/usr/bin/env python3
"""
CedroTech Market Data API Client
Proper implementation with session-based authentication for market data access
"""

import requests
import json
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()

class CedroTechMarketData:
    """
    CedroTech Market Data API Client with proper authentication
    """
    
    def __init__(self, platform_user=os.getenv('CEDROTECH_PLATAFORM'), platform_password=os.getenv('CEDROTECH_PLAT_PASSWORD')):
        """
        Initialize market data client with platform credentials
        
        Args:
            platform_user (str): Platform username
            platform_password (str): Platform password
        """
        self.platform_user = platform_user
        self.platform_password = platform_password
        self.session = None
        self.authenticated = False
        self.base_url = "https://webfeeder.cedrotech.com"
        
        print(f"🔌 CedroTech Market Data API initialized")
        print(f"   Platform User: {platform_user}")
        
    def authenticate(self):
        """
        Authenticate with CedroTech platform to get session cookies
        
        Returns:
            bool: True if authentication successful, False otherwise
        """
        print(f"🔐 Authenticating with CedroTech...")
        
        try:
            # Create session to maintain cookies
            self.session = requests.Session()
            
            # Authentication endpoint
            auth_url = f"{self.base_url}/SignIn"
            
            # Authentication parameters
            params = {
                "login": self.platform_user,
                "password": self.platform_password
            }
            
            headers = {
                "accept": "application/json"
            }
            
            # Make authentication request
            response = self.session.post(auth_url, headers=headers, params=params)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                # Check if we got session cookies
                cookies = dict(self.session.cookies)
                if cookies:
                    print(f"   ✅ Authentication successful!")
                    print(f"   🍪 Session cookies: {list(cookies.keys())}")
                    self.authenticated = True
                    return True
                else:
                    print(f"   ❌ No session cookies received")
                    return False
            else:
                print(f"   ❌ Authentication failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"   💥 Authentication error: {e}")
            return False
    
    def get_asset_quote(self, ticker):
        """
        Get quote data for a specific asset
        
        Args:
            ticker (str): Asset ticker (e.g., "PETR4", "VALE3")
            
        Returns:
            dict: Quote data or error information
        """
        if not self.authenticated or not self.session:
            print(f"❌ Not authenticated. Call authenticate() first.")
            return {"success": False, "error": "Not authenticated"}
        
        try:
            # Build URL according to documentation
            url = f"{self.base_url}/services/quotes/quote/{ticker}"
            
            headers = {
                "accept": "application/json"
            }
            
            print(f"📊 Getting quote for {ticker}...")
            print(f"   URL: {url}")
            
            # Make request using authenticated session
            response = self.session.get(url, headers=headers)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    quote_data = response.json()
                    print(f"   ✅ Quote data received for {ticker}")
                    
                    # Display key information
                    if isinstance(quote_data, dict):
                        price = quote_data.get('price', quote_data.get('last', 'N/A'))
                        change = quote_data.get('change', quote_data.get('variation', 'N/A'))
                        volume = quote_data.get('volume', 'N/A')
                        
                        print(f"   💰 Price: {price}")
                        print(f"   📈 Change: {change}")
                        print(f"   📊 Volume: {volume}")
                    
                    return {
                        "success": True,
                        "ticker": ticker,
                        "data": quote_data,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                except json.JSONDecodeError:
                    print(f"   ⚠️  Non-JSON response received")
                    print(f"   Raw response: {response.text[:200]}...")
                    
                    return {
                        "success": True,
                        "ticker": ticker,
                        "raw_response": response.text,
                        "timestamp": datetime.now().isoformat()
                    }
                    
            else:
                print(f"   ❌ Failed to get quote: {response.status_code}")
                print(f"   Error: {response.text[:100]}...")
                
                return {
                    "success": False,
                    "ticker": ticker,
                    "error": f"HTTP {response.status_code}",
                    "raw_response": response.text
                }
                
        except Exception as e:
            print(f"   💥 Error getting quote: {e}")
            return {
                "success": False,
                "ticker": ticker,
                "error": str(e)
            }
    
    def get_multiple_quotes(self, tickers):
        """
        Get quotes for multiple assets
        
        Args:
            tickers (list): List of asset tickers
            
        Returns:
            dict: Results for all tickers
        """
        results = {}
        
        for ticker in tickers:
            results[ticker] = self.get_asset_quote(ticker)
            
        return results
    
    def test_popular_assets(self):
        """
        Test getting quotes for popular Brazilian assets
        """
        print(f"\n🧪 TESTING POPULAR BRAZILIAN ASSETS")
        print("=" * 60)
        
        popular_assets = [
            "PETR4",  # Petrobras
            "VALE3",  # Vale
            "ITUB4",  # Itaú
            "BBDC4",  # Bradesco
            "ABEV3",  # Ambev
            "WEGE3",  # WEG
            "MGLU3",  # Magazine Luiza
            "PETR3",  # Petrobras PN
        ]
        
        results = self.get_multiple_quotes(popular_assets)
        
        print(f"\n📊 RESULTS SUMMARY:")
        print("-" * 40)
        
        successful = 0
        failed = 0
        
        for ticker, result in results.items():
            if result.get("success"):
                successful += 1
                data = result.get("data", {})
                if isinstance(data, dict):
                    price = data.get('price', data.get('last', 'N/A'))
                    print(f"   ✅ {ticker}: {price}")
                else:
                    print(f"   ✅ {ticker}: Data received")
            else:
                failed += 1
                error = result.get("error", "Unknown error")
                print(f"   ❌ {ticker}: {error}")
        
        print(f"\n📈 Success Rate: {successful}/{len(popular_assets)} ({successful/len(popular_assets)*100:.1f}%)")
        
        return results

def test_market_data_api():
    """
    Test the complete market data API functionality
    """
    print("🧪 CEDROTECH MARKET DATA API TEST")
    print("=" * 60)
    
    # Initialize market data client
    market_data = CedroTechMarketData()
    
    # Test authentication
    if not market_data.authenticate():
        print("❌ Authentication failed - cannot proceed with market data tests")
        return False
    
    # Test single asset quote
    print(f"\n📊 Testing single asset quote...")
    petr4_result = market_data.get_asset_quote("PETR4")
    
    # Test multiple assets
    market_data.test_popular_assets()
    
    return True

if __name__ == "__main__":
    test_market_data_api()
    
    print(f"\n🎯 INTEGRATION READY!")
    print("=" * 60)
    print("If the tests above were successful, you can now:")
    print("  1. ✅ Get real-time quotes for any Brazilian stock")
    print("  2. ✅ Integrate market data into your trading robot")
    print("  3. ✅ Make data-driven trading decisions")
    print("")
    print("💡 Next steps:")
    print("  - Add market data to your robot.py")
    print("  - Use real prices for position sizing")
    print("  - Create price-based trading signals")
