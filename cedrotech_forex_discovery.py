#!/usr/bin/env python3
"""
CedroTech Forex/Currency Discovery Tool
Discover available forex and currency instruments through CedroTech API
To potentially avoid monthly fees by maintaining forex contracts
"""

import requests
import json
import os
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class CedroTechForexDiscovery:
    """
    Discover forex/currency trading options available through CedroTech API
    """
    
    def __init__(self):
        self.base_url = "https://webfeeder.cedrotech.com"
        self.session = requests.Session()
        self.authenticated = False
        
        # Get credentials
        self.platform_user = os.getenv('CEDROTECH_PLATAFORM')
        self.platform_password = os.getenv('CEDROTECH_PLAT_PASSWORD')
        
        # Common forex symbols to test
        self.forex_symbols = [
            'USD', 'USDBRL', 'USD/BRL', 'DOLBRL', 'DOL',
            'EUR', 'EURBRL', 'EUR/BRL', 'EURBR', 
            'GBP', 'GBPBRL', 'GBP/BRL',
            'JPY', 'JPYBRL', 'JPY/BRL',
            'CHF', 'CHFBRL', 'CHF/BRL',
            'CAD', 'CADBRL', 'CAD/BRL',
            'AUD', 'AUDBRL', 'AUD/BRL',
            'WINFUT', 'WINJ25', 'WINZ24',  # Mini Dollar futures
            'DOLFUT', 'DOLJ25', 'DOLZ24',  # Full Dollar futures
            'EURF', 'EURJ25', 'EURZ24',    # Euro futures
        ]
        
        # Set headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Connection': 'keep-alive'
        })
        
        self.results = {}
    
    def authenticate(self) -> bool:
        """Authenticate with CedroTech platform"""
        print("🔐 AUTHENTICATING WITH CEDROTECH...")
        
        if not self.platform_user or not self.platform_password:
            print("❌ Missing credentials! Check environment variables")
            return False
        
        try:
            auth_url = f"{self.base_url}/SignIn"
            params = {
                "login": self.platform_user,
                "password": self.platform_password
            }
            
            response = self.session.post(auth_url, headers={"accept": "application/json"}, params=params)
            
            if response.status_code == 200 and dict(self.session.cookies):
                print("✅ Authentication successful!")
                self.authenticated = True
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def discover_markets(self) -> List[Dict]:
        """Discover all available markets"""
        print("\n🌍 DISCOVERING AVAILABLE MARKETS...")
        
        if not self.authenticated:
            if not self.authenticate():
                return []
        
        try:
            url = f"{self.base_url}/services/quotes/listMarket"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                markets = response.json()
                print(f"✅ Found {len(markets) if isinstance(markets, list) else 'unknown'} markets")
                
                # Look for forex/currency related markets
                forex_markets = []
                if isinstance(markets, list):
                    for market in markets:
                        if isinstance(market, dict):
                            name = str(market.get('name', '')).upper()
                            description = str(market.get('description', '')).upper()
                            
                            # Check for forex-related keywords
                            forex_keywords = ['FOREX', 'CURRENCY', 'CAMBIO', 'DOLAR', 'DOLLAR', 'MOEDA', 'FX']
                            if any(keyword in name or keyword in description for keyword in forex_keywords):
                                forex_markets.append(market)
                                print(f"🏦 FOREX MARKET FOUND: {market}")
                
                self.results['markets'] = markets
                self.results['forex_markets'] = forex_markets
                
                if forex_markets:
                    print(f"🎯 Found {len(forex_markets)} potential forex markets!")
                else:
                    print("⚠️ No obvious forex markets found, checking other markets...")
                
                return markets
            else:
                print(f"❌ Failed to get markets: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error discovering markets: {e}")
            return []
    
    def test_forex_symbols(self) -> Dict[str, Any]:
        """Test various forex symbols to see what's available"""
        print("\n💱 TESTING FOREX SYMBOLS...")
        
        if not self.authenticated:
            if not self.authenticate():
                return {}
        
        found_symbols = {}
        
        for symbol in self.forex_symbols:
            print(f"   Testing: {symbol}")
            
            try:
                # Test quote endpoint
                url = f"{self.base_url}/services/quotes/quote/{symbol}"
                response = self.session.get(url, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    if data and not (isinstance(data, dict) and data.get('error')):
                        found_symbols[symbol] = {
                            'type': 'quote',
                            'data': data,
                            'url': url
                        }
                        print(f"   ✅ {symbol}: FOUND in quotes!")
                        
                        # If it's a quote, get more details
                        if isinstance(data, dict):
                            print(f"      Price: {data.get('price', 'N/A')}")
                            print(f"      Name: {data.get('name', 'N/A')}")
                
                # Test company quotes (for options/derivatives)
                url2 = f"{self.base_url}/services/quotes/companyQuotes?company={symbol}&types=2&markets=1"
                response2 = self.session.get(url2, timeout=5)
                
                if response2.status_code == 200:
                    data2 = response2.json()
                    if data2 and isinstance(data2, list) and len(data2) > 0:
                        if symbol not in found_symbols:
                            found_symbols[symbol] = {}
                        found_symbols[symbol]['derivatives'] = data2
                        print(f"   ✅ {symbol}: Found {len(data2)} derivatives/options!")
                
                time.sleep(0.2)  # Be respectful to API
                
            except Exception as e:
                print(f"   ❌ {symbol}: Error - {e}")
                continue
        
        self.results['forex_symbols'] = found_symbols
        return found_symbols
    
    def check_bmf_futures(self) -> Dict[str, Any]:
        """Check BM&F futures market for currency contracts"""
        print("\n🏛️ CHECKING BM&F FUTURES FOR CURRENCY CONTRACTS...")
        
        if not self.authenticated:
            if not self.authenticate():
                return {}
        
        bmf_symbols = [
            'WDO', 'WDO25', 'WDO24',  # Mini Dollar
            'DOL', 'DOL25', 'DOL24',  # Full Dollar
            'IND', 'IND25', 'IND24',  # Ibovespa
            'WIN', 'WIN25', 'WIN24',  # Mini Ibovespa  
            'EUR', 'EUR25', 'EUR24',  # Euro
            'WINx25', 'WINz24', 'WINj25',  # Win specific months
            'WDOx25', 'WDOz24', 'WDOj25',  # Mini Dollar specific months
        ]
        
        futures_found = {}
        
        for symbol in bmf_symbols:
            print(f"   Testing BM&F: {symbol}")
            
            try:
                url = f"{self.base_url}/services/quotes/quote/{symbol}"
                response = self.session.get(url, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    if data and not (isinstance(data, dict) and data.get('error')):
                        futures_found[symbol] = data
                        print(f"   ✅ {symbol}: FOUND!")
                        
                        if isinstance(data, dict):
                            print(f"      Price: {data.get('price', 'N/A')}")
                            print(f"      Volume: {data.get('volume', 'N/A')}")
                
                time.sleep(0.2)
                
            except Exception as e:
                continue
        
        self.results['bmf_futures'] = futures_found
        return futures_found
    
    def discover_all_forex_options(self):
        """Run complete forex discovery"""
        print("🚀 CEDROTECH FOREX/CURRENCY DISCOVERY")
        print("=" * 60)
        print("🎯 Goal: Find forex instruments to maintain monthly contracts")
        print("💰 Benefit: Avoid CedroTech monthly fees with BTG Pactual")
        print("=" * 60)
        
        # Step 1: Authenticate
        if not self.authenticate():
            print("❌ Cannot proceed without authentication")
            return
        
        # Step 2: Discover markets
        markets = self.discover_markets()
        
        # Step 3: Test forex symbols
        forex_symbols = self.test_forex_symbols()
        
        # Step 4: Check BM&F futures
        bmf_futures = self.check_bmf_futures()
        
        # Step 5: Generate summary
        self.generate_summary()
        self.save_results()
    
    def generate_summary(self):
        """Generate comprehensive summary"""
        print("\n" + "="*60)
        print("📊 FOREX DISCOVERY SUMMARY")
        print("="*60)
        
        forex_symbols = self.results.get('forex_symbols', {})
        bmf_futures = self.results.get('bmf_futures', {})
        forex_markets = self.results.get('forex_markets', [])
        
        print(f"🏦 Forex Markets Found: {len(forex_markets)}")
        print(f"💱 Forex Symbols Found: {len(forex_symbols)}")
        print(f"🏛️ BM&F Futures Found: {len(bmf_futures)}")
        
        if forex_markets:
            print(f"\n🏦 FOREX MARKETS:")
            for market in forex_markets:
                print(f"   🔹 {market.get('name', 'Unknown')} - {market.get('description', 'No description')}")
        
        if forex_symbols:
            print(f"\n💱 AVAILABLE FOREX SYMBOLS:")
            for symbol, data in forex_symbols.items():
                price_info = ""
                if 'data' in data and isinstance(data['data'], dict):
                    price = data['data'].get('price')
                    if price:
                        price_info = f" (Price: {price})"
                
                derivatives_info = ""
                if 'derivatives' in data:
                    derivatives_info = f" + {len(data['derivatives'])} derivatives"
                
                print(f"   💰 {symbol}{price_info}{derivatives_info}")
        
        if bmf_futures:
            print(f"\n🏛️ BM&F CURRENCY FUTURES:")
            for symbol, data in bmf_futures.items():
                price_info = ""
                volume_info = ""
                if isinstance(data, dict):
                    price = data.get('price')
                    volume = data.get('volume')
                    if price:
                        price_info = f" (Price: {price})"
                    if volume:
                        volume_info = f" (Vol: {volume})"
                
                print(f"   📈 {symbol}{price_info}{volume_info}")
        
        # Recommendations
        print(f"\n🎯 RECOMMENDATIONS FOR MONTHLY FOREX CONTRACTS:")
        
        if bmf_futures:
            print("   ✅ BM&F Currency Futures (Recommended):")
            for symbol in bmf_futures.keys():
                if 'WDO' in symbol:
                    print(f"      🥇 {symbol} - Mini Dollar (Lower margin requirement)")
                elif 'DOL' in symbol:
                    print(f"      🥈 {symbol} - Full Dollar (Higher margin requirement)")
                elif 'EUR' in symbol:
                    print(f"      🥉 {symbol} - Euro Future")
        
        if forex_symbols:
            print("   ✅ Alternative Forex Options:")
            for symbol in forex_symbols.keys():
                if 'USD' in symbol or 'DOL' in symbol:
                    print(f"      💵 {symbol} - USD related")
        
        total_options = len(forex_symbols) + len(bmf_futures) + len(forex_markets)
        
        if total_options > 0:
            print(f"\n🎉 SUCCESS! Found {total_options} forex trading options!")
            print("💡 You can use these to maintain monthly contracts and avoid CedroTech fees!")
        else:
            print(f"\n⚠️ No forex options found. May need to check with BTG Pactual about available instruments.")
    
    def save_results(self):
        """Save results to JSON file"""
        filename = f"cedrotech_forex_discovery_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        output = {
            'discovery_metadata': {
                'timestamp': datetime.now().isoformat(),
                'goal': 'Find forex instruments for monthly contracts to avoid CedroTech fees',
                'broker': 'BTG Pactual',
                'api_base': self.base_url
            },
            'results': self.results,
            'summary': {
                'forex_markets_count': len(self.results.get('forex_markets', [])),
                'forex_symbols_count': len(self.results.get('forex_symbols', {})),
                'bmf_futures_count': len(self.results.get('bmf_futures', {})),
                'total_options': len(self.results.get('forex_markets', [])) + 
                               len(self.results.get('forex_symbols', {})) + 
                               len(self.results.get('bmf_futures', {}))
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Results saved to: {filename}")

def main():
    """Main function"""
    discovery = CedroTechForexDiscovery()
    discovery.discover_all_forex_options()

if __name__ == "__main__":
    main()
