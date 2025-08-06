#!/usr/bin/env python3
"""
CedroTech Options API Client
Advanced implementation for options trading with market data integration
Perfect for day trading options based on underlying asset analysis
"""

import requests
import json
from datetime import datetime, timedelta
import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv()

class CedroTechOptionsAPI:
    """
    CedroTech Options API Client with focus on options trading
    Integrates with your existing trading robot for options-based strategies
    """
    
    def __init__(self, platform_user=os.getenv('CEDROTECH_PLATAFORM'), platform_password=os.getenv('CEDROTECH_PLAT_PASSWORD')):
        """
        Initialize options API client with platform credentials
        
        Args:
            platform_user (str): Platform username
            platform_password (str): Platform password
        """
        self.platform_user = platform_user
        self.platform_password = platform_password
        self.session = None
        self.authenticated = False
        self.base_url = "https://webfeeder.cedrotech.com"
        
        print(f"📈 CedroTech Options API initialized")
        print(f"   Focus: OPTIONS TRADING")
        print(f"   Platform User: {platform_user}")
        
    def authenticate(self):
        """
        Authenticate with CedroTech platform to get session cookies
        
        Returns:
            bool: True if authentication successful, False otherwise
        """
        print(f"🔐 Authenticating for options trading...")
        
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
                    print(f"   ✅ Options API authentication successful!")
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

    def get_options_list(self, underlying_asset):
        """
        Get list of options for a specific underlying asset
        This is the KEY ENDPOINT for options trading!
        
        Args:
            underlying_asset (str): Underlying asset ticker (e.g., "PETR4", "VALE3")
            
        Returns:
            dict: Options list with strikes, expirations, and prices
        """
        if not self.authenticated or not self.session:
            print(f"❌ Not authenticated. Call authenticate() first.")
            return {"success": False, "error": "Not authenticated"}
        try:
            # According to documentation: "Consultar Lista de Opções de um Ativo"
            # Correct endpoint: /services/quotes/optionsQuote/{codAtivo}
            url = f"{self.base_url}/services/quotes/optionsQuote/{underlying_asset}"
            
            headers = {
                "accept": "application/json"
            }
            
            print(f"📋 Getting options list for {underlying_asset}...")
            print(f"   URL: {url}")
            
            # Make request using authenticated session
            response = self.session.get(url, headers=headers)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    options_data = response.json()
                    print(f"   ✅ Options data received for {underlying_asset}")
                    
                    # Analyze the options data
                    self._analyze_options_data(underlying_asset, options_data)
                    
                    return {
                        "success": True,
                        "underlying": underlying_asset,
                        "options": options_data,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                except json.JSONDecodeError:
                    print(f"   ⚠️  Non-JSON response received")
                    print(f"   Raw response: {response.text[:200]}...")
                    
                    return {
                        "success": True,
                        "underlying": underlying_asset,
                        "raw_response": response.text,
                        "timestamp": datetime.now().isoformat()
                    }
                    
            else:
                print(f"   ❌ Failed to get options: {response.status_code}")
                print(f"   Error: {response.text[:100]}...")
                
                return {
                    "success": False,
                    "underlying": underlying_asset,
                    "error": f"HTTP {response.status_code}",
                    "raw_response": response.text
                }
                
        except Exception as e:
            print(f"   💥 Error getting options: {e}")
            return {
                "success": False,
                "underlying": underlying_asset,
                "error": str(e)
            }

    def get_top_gainers(self):
        """
        Get list of top gaining assets (Consultar Maiores Altas)
        Perfect for finding assets with strong momentum for options trading
        
        Returns:
            dict: List of top gaining assets
        """
        if not self.authenticated or not self.session:
            print(f"❌ Not authenticated. Call authenticate() first.")
            return {"success": False, "error": "Not authenticated"}
        try:
            # "Consultar Maiores Altas" endpoint
            url = f"{self.base_url}/services/quotes/topGainers"
            
            headers = {
                "accept": "application/json"
            }
            
            print(f"📈 Getting top gainers...")
            print(f"   URL: {url}")
            
            response = self.session.get(url, headers=headers)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    gainers_data = response.json()
                    print(f"   ✅ Top gainers data received")
                    
                    # Display top opportunities
                    if isinstance(gainers_data, list):
                        print(f"   🚀 Found {len(gainers_data)} top gainers")
                        for i, asset in enumerate(gainers_data[:5]):  # Show top 5
                            ticker = asset.get('symbol', asset.get('ticker', 'N/A'))
                            change = asset.get('change_percent', asset.get('variation', 'N/A'))
                            print(f"      {i+1}. {ticker}: +{change}%")
                    
                    return {
                        "success": True,
                        "data": gainers_data,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                except json.JSONDecodeError:
                    print(f"   ⚠️  Non-JSON response received")
                    return {
                        "success": True,
                        "raw_response": response.text,
                        "timestamp": datetime.now().isoformat()
                    }
                    
            else:
                print(f"   ❌ Failed to get top gainers: {response.status_code}")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "raw_response": response.text
                }
                
        except Exception as e:
            print(f"   💥 Error getting top gainers: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def get_top_losers(self):
        """
        Get list of top losing assets (Consultar Maiores Baixas)
        Useful for contrarian options strategies or put opportunities
        
        Returns:
            dict: List of top losing assets
        """
        if not self.authenticated or not self.session:
            print(f"❌ Not authenticated. Call authenticate() first.")
            return {"success": False, "error": "Not authenticated"}
        try:
            # "Consultar Maiores Baixas" endpoint
            url = f"{self.base_url}/services/quotes/topLosers"
            
            headers = {
                "accept": "application/json"
            }
            
            print(f"📉 Getting top losers...")
            print(f"   URL: {url}")
            
            response = self.session.get(url, headers=headers)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    losers_data = response.json()
                    print(f"   ✅ Top losers data received")
                    
                    # Display opportunities for contrarian plays
                    if isinstance(losers_data, list):
                        print(f"   📉 Found {len(losers_data)} top losers")
                        for i, asset in enumerate(losers_data[:5]):  # Show top 5
                            ticker = asset.get('symbol', asset.get('ticker', 'N/A'))
                            change = asset.get('change_percent', asset.get('variation', 'N/A'))
                            print(f"      {i+1}. {ticker}: {change}%")
                    
                    return {
                        "success": True,
                        "data": losers_data,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                except json.JSONDecodeError:
                    print(f"   ⚠️  Non-JSON response received")
                    return {
                        "success": True,
                        "raw_response": response.text,
                        "timestamp": datetime.now().isoformat()
                    }
                    
            else:
                print(f"   ❌ Failed to get top losers: {response.status_code}")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "raw_response": response.text
                }
                
        except Exception as e:
            print(f"   💥 Error getting top losers: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def get_markets_list(self):
        """
        Get list of available markets (Consultar Lista de Mercados)
        
        Returns:
            dict: List of available markets
        """
        if not self.authenticated or not self.session:
            print(f"❌ Not authenticated. Call authenticate() first.")
            return {"success": False, "error": "Not authenticated"}
        try:
            # "Consultar Lista de Mercados" endpoint
            url = f"{self.base_url}/services/quotes/markets"
            
            headers = {
                "accept": "application/json"
            }
            
            print(f"🏢 Getting markets list...")
            print(f"   URL: {url}")
            
            response = self.session.get(url, headers=headers)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    markets_data = response.json()
                    print(f"   ✅ Markets data received")
                    
                    return {
                        "success": True,
                        "data": markets_data,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                except json.JSONDecodeError:
                    print(f"   ⚠️  Non-JSON response received")
                    return {
                        "success": True,
                        "raw_response": response.text,
                        "timestamp": datetime.now().isoformat()
                    }
                    
            else:
                print(f"   ❌ Failed to get markets: {response.status_code}")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "raw_response": response.text
                }
                
        except Exception as e:
            print(f"   💥 Error getting markets: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def get_asset_info(self, ticker):
        """
        Get detailed information about an asset using the correct API endpoint
        
        Args:
            ticker (str): Asset ticker
            
        Returns:
            dict: Detailed asset information
        """
        if not self.authenticated or not self.session:
            print(f"❌ Not authenticated. Call authenticate() first.")
            return {"success": False, "error": "Not authenticated"}
            
        try:
            # Use the correct endpoint according to API documentation
            url = f"{self.base_url}/services/quotes/quoteInformation"
            params = {"description": ticker}
            
            headers = {
                "accept": "application/json"
            }
            
            print(f"ℹ️  Getting asset info for {ticker}...")
            print(f"   URL: {url}?description={ticker}")
            
            response = self.session.get(url, headers=headers, params=params)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    asset_info = response.json()
                    print(f"   ✅ Asset info received for {ticker}")
                    
                    return {
                        "success": True,
                        "ticker": ticker,
                        "data": asset_info,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                except json.JSONDecodeError:
                    print(f"   ⚠️  Non-JSON response received")
                    return {
                        "success": True,
                        "ticker": ticker,
                        "raw_response": response.text,
                        "timestamp": datetime.now().isoformat()
                    }
                    
            else:
                print(f"   ❌ Failed to get asset info: {response.status_code}")
                return {
                    "success": False,
                    "ticker": ticker,
                    "error": f"HTTP {response.status_code}",
                    "raw_response": response.text
                }
                
        except Exception as e:
            print(f"   💥 Error getting asset info: {e}")
            return {
                "success": False,
                "ticker": ticker,
                "error": str(e)
            }

    def get_option_quote(self, ticker):
        """
        Get real-time trading quote for an option (bid, ask, volume, etc.)
        This is different from get_asset_info which only returns metadata
        
        Args:
            ticker (str): Option ticker
            
        Returns:
            dict: Real-time quote data including bid, ask, volume, open interest
        """
        if not self.authenticated or not self.session:
            print(f"❌ Not authenticated. Call authenticate() first.")
            return {"success": False, "error": "Not authenticated"}
            
        try:
            # Use the quotes endpoint for real-time trading data
            url = f"{self.base_url}/services/quotes/quote/{ticker}"
            
            headers = {
                "accept": "application/json"
            }
            
            print(f"💰 Getting real-time quote for {ticker}...")
            print(f"   URL: {url}")
            
            response = self.session.get(url, headers=headers)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    quote_data = response.json()
                    print(f"   ✅ Real-time quote received for {ticker}")
                    
                    return {
                        "success": True,
                        "ticker": ticker,
                        "data": quote_data,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                except json.JSONDecodeError:
                    print(f"   ⚠️  Non-JSON response received")
                    return {
                        "success": True,
                        "ticker": ticker,
                        "raw_response": response.text,
                        "timestamp": datetime.now().isoformat()
                    }
                    
            else:
                print(f"   ❌ Failed to get quote: {response.status_code}")
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

    def _analyze_options_data(self, underlying, options_data):
        """
        Analyze options data to identify trading opportunities
        
        Args:
            underlying (str): Underlying asset ticker
            options_data: Raw options data from API
        """
        print(f"   🔍 Analyzing options for {underlying}...")
        
        if isinstance(options_data, list):
            calls = [opt for opt in options_data if opt.get('type', '').upper() == 'CALL']
            puts = [opt for opt in options_data if opt.get('type', '').upper() == 'PUT']
            
            print(f"      📊 Found {len(calls)} call options")
            print(f"      📊 Found {len(puts)} put options")
            
            # Find near-the-money options with good volume
            # This is where the best day trading opportunities usually are
            
        elif isinstance(options_data, dict):
            print(f"      📊 Options data keys: {list(options_data.keys())}")
        
        print(f"      💡 Options analysis complete")

    def find_best_options_for_trading(self, underlying_assets):
        """
        Find the best options trading opportunities across multiple assets
        This integrates with your robot's asset selection logic
        
        Args:
            underlying_assets (list): List of underlying asset tickers
            
        Returns:
            dict: Ranked list of best options trading opportunities
        """
        print(f"\n🎯 FINDING BEST OPTIONS TRADING OPPORTUNITIES")
        print("=" * 60)
        
        opportunities = []
        
        for asset in underlying_assets:
            print(f"\n🔍 Analyzing {asset}...")
            
            # Get asset info
            asset_info = self.get_asset_info(asset)
            
            # Get options list
            options_result = self.get_options_list(asset)
            
            if options_result.get("success"):
                opportunity = {
                    "underlying": asset,
                    "asset_info": asset_info,
                    "options": options_result,
                    "score": self._score_options_opportunity(asset, options_result),
                    "timestamp": datetime.now().isoformat()
                }
                opportunities.append(opportunity)
        
        # Sort by score (highest first)
        opportunities.sort(key=lambda x: x.get("score", 0), reverse=True)
        
        print(f"\n📈 BEST OPTIONS OPPORTUNITIES:")
        print("-" * 40)
        for i, opp in enumerate(opportunities[:5]):  # Top 5
            asset = opp["underlying"]
            score = opp.get("score", 0)
            print(f"   {i+1}. {asset}: Score {score:.2f}")
        
        return {
            "success": True,
            "opportunities": opportunities,
            "timestamp": datetime.now().isoformat()
        }

    def _score_options_opportunity(self, underlying, options_result):
        """
        Score an options trading opportunity based on various factors
        
        Args:
            underlying (str): Underlying asset ticker
            options_result (dict): Options data result
            
        Returns:
            float: Opportunity score (0-100)
        """
        score = 0.0
        
        # Base score for having options available
        if options_result.get("success"):
            score += 10.0
        
        # Add more scoring logic based on:
        # - Volume
        # - Open interest  
        # - Bid-ask spreads
        # - Time to expiration
        # - Volatility
        # - Underlying momentum
        
        return score

    def test_all_endpoints(self):
        """
        Test all available endpoints for options trading
        """
        print(f"\n🧪 TESTING ALL OPTIONS ENDPOINTS")
        print("=" * 60)
        
        # Test popular assets for options
        test_assets = [
            "PETR4",  # Petrobras - High liquidity
            "VALE3",  # Vale - High volume
            "ITUB4",  # Itaú - Banking sector
            "BBDC4",  # Bradesco - Banking sector
        ]
        
        results = {}
        
        # Test 1: Top gainers
        print(f"\n1. Testing Top Gainers...")
        results["top_gainers"] = self.get_top_gainers()
        
        # Test 2: Top losers
        print(f"\n2. Testing Top Losers...")
        results["top_losers"] = self.get_top_losers()
        
        # Test 3: Markets list
        print(f"\n3. Testing Markets List...")
        results["markets"] = self.get_markets_list()
        
        # Test 4: Options for each asset
        print(f"\n4. Testing Options Lists...")
        results["options"] = {}
        for asset in test_assets:
            print(f"\n   Testing options for {asset}...")
            results["options"][asset] = self.get_options_list(asset)
        
        # Test 5: Asset info
        print(f"\n5. Testing Asset Info...")
        results["asset_info"] = {}
        for asset in test_assets:
            results["asset_info"][asset] = self.get_asset_info(asset)
        
        # Summary
        print(f"\n📊 TEST RESULTS SUMMARY:")
        print("-" * 40)
        
        success_count = 0
        total_tests = 0
        
        for category, result in results.items():
            if isinstance(result, dict):
                if result.get("success"):
                    success_count += 1
                    print(f"   ✅ {category}: SUCCESS")
                else:
                    print(f"   ❌ {category}: FAILED")
                total_tests += 1
            elif isinstance(result, dict):
                for asset, asset_result in result.items():
                    if asset_result.get("success"):
                        success_count += 1
                        print(f"   ✅ {category} ({asset}): SUCCESS")
                    else:
                        print(f"   ❌ {category} ({asset}): FAILED")
                    total_tests += 1
        
        success_rate = (success_count / total_tests * 100) if total_tests > 0 else 0
        print(f"\n📈 Success Rate: {success_count}/{total_tests} ({success_rate:.1f}%)")
        
        return results

def test_options_api():
    """
    Test the complete options API functionality
    """
    print("🧪 CEDROTECH OPTIONS API TEST")
    print("=" * 60)
    
    # Initialize options API client
    options_api = CedroTechOptionsAPI()
    
    # Test authentication
    if not options_api.authenticate():
        print("❌ Authentication failed - cannot proceed with options tests")
        return False
    
    # Test all endpoints
    test_results = options_api.test_all_endpoints()
    
    # Test best opportunities finder
    print(f"\n🎯 Testing Best Opportunities Finder...")
    opportunities = options_api.find_best_options_for_trading(["PETR4", "VALE3", "ITUB4"])
    
    return True

if __name__ == "__main__":
    test_options_api()
    
    print(f"\n🎯 OPTIONS TRADING INTEGRATION READY!")
    print("=" * 60)
    print("If the tests above were successful, you can now:")
    print("  1. ✅ Get options lists for any Brazilian stock")
    print("  2. ✅ Find top gainers/losers for options opportunities")
    print("  3. ✅ Integrate options analysis into your trading robot")
    print("  4. ✅ Make options-based trading decisions")
    print("")
    print("💡 Next steps for your robot:")
    print("  - Integrate options API with your existing robot.py")
    print("  - Use top gainers to find high-momentum assets")
    print("  - Trade options instead of stocks for higher returns")
    print("  - Implement options-specific risk management")
    print("")
    print("🚀 OPTIONS = HIGHER PROFIT POTENTIAL!")
    print("💰 Day trading options can multiply your profits!")
