"""
FINAL OPTIONS DISCOVERY SYSTEM
=============================

Production-ready options discovery using real CedroTech API endpoints.
This system uses actual market data with proper field mapping discovered through API debugging.

Features:
- Uses working /services/quotes/companyQuotes endpoint
- Gets real quotes via /services/quotes/quote/{ticker} 
- Proper field mapping: volumeAmount, interest, bid, ask, etc.
- Quality analysis and filtering
- Robot-ready format
"""

import json
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any

from cedrotech_options_api import CedroTechOptionsAPI
from options_filter_analysis import OptionsTradeabilityAnalyzer


class FinalOptionsDiscovery:
    """Production-ready options discovery with validated API endpoints"""
    
    def __init__(self):
        self.options_api = CedroTechOptionsAPI()
        self.analyzer = OptionsTradeabilityAnalyzer()
        
        # Major Ibovespa underlyings
        self.underlyings = [
            'VALE3', 'PETR4', 'ITUB4', 'BBAS3', 'B3SA3',
            'ABEV3', 'MGLU3', 'WEGE3', 'RENT3', 'LREN3'
        ]
        
        # Company name mapping (discovered through API testing)
        self.company_mapping = {
            'VALE3': 'VALE',
            'PETR4': 'PETROBRAS', 
            'ITUB4': 'ITAU',
            'BBAS3': 'BRADESCO',
            'B3SA3': 'B3',
            'ABEV3': 'AMBEV',
            'MGLU3': 'MAGAZINE',
            'WEGE3': 'WEG',
            'RENT3': 'LOCALIZA',
            'LREN3': 'LOJAS'
        }
        
    def discover_active_options(self) -> Dict[str, Any]:
        """Discover active options with real market data"""
        print("🚀 FINAL OPTIONS DISCOVERY - PRODUCTION SYSTEM")
        print("=" * 70)
        
        if not self.options_api.authenticate():
            print("❌ Failed to authenticate with CedroTech API")
            return {}
        
        discovered_options = {}
        total_options = 0
        
        for underlying in self.underlyings:
            company_name = self.company_mapping.get(underlying, underlying.replace('3', '').replace('4', ''))
            print(f"\n📊 Discovering options for {underlying} (company: {company_name})...")
            
            options = self._get_company_options(company_name, underlying)
            
            if options:
                discovered_options[underlying] = {"options": options}
                total_options += len(options)
                print(f"   ✅ Found {len(options)} active options for {underlying}")
                
                # Show sample
                for i, opt in enumerate(options[:2]):
                    quotes_info = "No quotes" if opt['bid'] == 0 and opt['ask'] == 0 else f"Bid: {opt['bid']:.2f}, Ask: {opt['ask']:.2f}"
                    print(f"      {i+1}. {opt['symbol']} - {quotes_info}, OI: {opt['open_interest']:,}")
            else:
                print(f"   ⚠️ No options found for {underlying}")
        
        print(f"\n🎯 DISCOVERY SUMMARY:")
        print(f"   Total active options: {total_options}")
        print(f"   Underlyings with options: {len(discovered_options)}")
        
        return discovered_options
    
    def _get_company_options(self, company_name: str, underlying: str) -> List[Dict[str, Any]]:
        """Get options for company using validated API endpoint"""
        try:
            session = self.options_api.session
            base_url = self.options_api.base_url
            
            # Validated endpoint from API testing
            company_url = f"{base_url}/services/quotes/companyQuotes"
            params = {
                "company": company_name,
                "types": "2",  # Options type
                "markets": "1"  # Bovespa market
            }
            headers = {"accept": "application/json"}
            
            response = session.get(company_url, headers=headers, params=params)
            
            if response.status_code == 200:
                try:
                    symbols = response.json()
                    
                    if isinstance(symbols, list) and symbols:
                        print(f"   📋 Found {len(symbols)} option symbols")
                        
                        # Get real quotes for each symbol (limit to 40 for performance)
                        active_options = []
                        for i, symbol in enumerate(symbols[:40]):
                            option_data = self._get_option_quote(symbol, underlying)
                            if option_data:
                                active_options.append(option_data)
                            
                            # Progress update
                            if (i + 1) % 10 == 0:
                                print(f"      📊 Processed {i + 1}/{min(40, len(symbols))} options...")
                        
                        print(f"   💰 Got quotes for {len(active_options)} options")
                        return active_options
                    else:
                        print(f"   ⚠️ No symbols returned")
                        return []
                        
                except json.JSONDecodeError:
                    print(f"   ❌ Invalid JSON response")
                    return []
            else:
                print(f"   ❌ API request failed: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"   💥 Error: {e}")
            return []
    
    def _get_option_quote(self, symbol: str, underlying: str) -> Optional[Dict[str, Any]]:
        """Get real quote data for option symbol"""
        try:
            # Use the working get_option_quote method
            result = self.options_api.get_option_quote(symbol)
            
            if not result or 'data' not in result:
                return None
            
            data = result['data']
            
            # Extract data using validated field names from API debugging
            bid = float(data.get('bid', 0) or 0)
            ask = float(data.get('ask', 0) or 0)
            last_trade = float(data.get('lastTrade', 0) or 0)
            volume = int(data.get('volumeAmount', 0) or 0)  # Validated field name
            open_interest = int(data.get('interest', 0) or 0)  # Validated field name
            
            # Additional option metadata
            option_type = data.get('typeOption', 'unknown')  # Call/Put type
            direction = data.get('directionOption', 'unknown')  # Direction indicator
            company = data.get('company', '')
            contract_multiplier = data.get('contractMultiplier', 1)
            
            # Market data quality indicators
            has_real_quotes = bid > 0 or ask > 0 or last_trade > 0
            has_volume = volume > 0
            has_open_interest = open_interest > 0
            
            option_data = {
                'symbol': symbol,
                'underlying': underlying,
                'bid': bid,
                'ask': ask,
                'last_trade': last_trade,
                'volume': volume,
                'open_interest': open_interest,
                'option_type': option_type,
                'direction': direction,
                'company': company,
                'contract_multiplier': contract_multiplier,
                'has_real_quotes': has_real_quotes,
                'has_volume': has_volume,
                'has_open_interest': has_open_interest,
                'discovery_timestamp': datetime.now().isoformat()
            }
            
            return option_data
            
        except Exception as e:
            return None
    
    def get_daily_tradeable_options(self, max_options: int = 20) -> List[Dict[str, Any]]:
        """Get daily tradeable options with quality analysis"""
        print("🎯 GETTING DAILY TRADEABLE OPTIONS")
        print("=" * 80)
        
        # Discover active options
        discovered = self.discover_active_options()
        if not discovered:
            print("❌ No options discovered")
            return []
        
        # Apply quality analysis
        print("\n📊 APPLYING QUALITY ANALYSIS...")
        analyzed = self.analyzer.filter_tradeable_options(discovered)
        
        if not analyzed.get('tradeable_options'):
            print("❌ No tradeable options after analysis")
            return []
        
        # Convert to robot format
        robot_options = []
        for option in analyzed['tradeable_options'][:max_options]:
            data = option['option_data']
            
            robot_option = {
                'symbol': data['symbol'],
                'underlying': data['underlying'],
                'score': option['quality_score'],
                'rating': option['overall_rating'],
                'liquidity_rating': option['liquidity_rating'],
                'open_interest': data['open_interest'],
                'volume': data['volume'],
                'bid': data['bid'],
                'ask': data['ask'],
                'last_trade': data['last_trade'],
                'spread_pct': ((data['ask'] - data['bid']) / data['ask'] * 100) if data['ask'] > 0 else 0,
                'option_type': data.get('option_type', 'unknown'),
                'direction': data.get('direction', 'unknown'),
                'company': data.get('company', ''),
                'discovery_timestamp': data['discovery_timestamp'],
                'strengths': option['strengths'],
                'warnings': option['warnings'],
                'is_real_option': True,
                'has_real_quotes': data['has_real_quotes'],
                'discovery_method': 'final_production'
            }
            
            robot_options.append(robot_option)
        
        # Summary
        print(f"\n🏆 FINAL RESULTS:")
        print(f"   Found {len(robot_options)} tradeable options ready for robot")
        
        if robot_options:
            print("\n📋 Top 5 options:")
            for i, opt in enumerate(robot_options[:5]):
                quotes = f"Bid: {opt['bid']:.2f}, Ask: {opt['ask']:.2f}" if opt['bid'] > 0 or opt['ask'] > 0 else "No quotes"
                print(f"   {i+1}. {opt['symbol']} ({opt['underlying']}) - Score: {opt['score']}/100")
                print(f"      {quotes} | OI: {opt['open_interest']:,} | Vol: {opt['volume']} | Spread: {opt['spread_pct']:.1f}%")
        
        # Save results
        self._save_results(discovered, robot_options)
        
        return robot_options
    
    def _save_results(self, discovered: Dict, robot_options: List[Dict]):
        """Save discovery results to file"""
        total_discovered = sum(len(v['options']) for v in discovered.values())
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'discovery_method': 'final_production',
            'total_discovered': total_discovered,
            'tradeable_count': len(robot_options),
            'robot_options': robot_options,
            'notes': 'Production system using validated API endpoints and field mapping'
        }
        
        with open('final_options_discovery.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Results saved to: final_options_discovery.json")


def main():
    """Test the final production discovery system"""
    print("🚀 TESTING FINAL PRODUCTION OPTIONS DISCOVERY")
    print("=" * 80)
    
    discovery = FinalOptionsDiscovery()
    options = discovery.get_daily_tradeable_options(max_options=25)
    
    if options:
        print(f"\n✅ SUCCESS: Found {len(options)} tradeable options!")
        print("🎯 Production system ready for robot integration")
        
        # Analytics
        by_underlying = {}
        options_with_quotes = 0
        options_with_oi = 0
        
        for opt in options:
            underlying = opt['underlying']
            by_underlying[underlying] = by_underlying.get(underlying, 0) + 1
            
            if opt['has_real_quotes']:
                options_with_quotes += 1
            if opt['open_interest'] > 0:
                options_with_oi += 1
        
        print(f"\n📊 Analytics:")
        print(f"   Options with quotes: {options_with_quotes}/{len(options)}")
        print(f"   Options with open interest: {options_with_oi}/{len(options)}")
        print(f"   Options by underlying: {dict(by_underlying)}")
        
        if options_with_quotes == 0:
            print(f"\n⏰ Note: Zero quotes likely means market is closed")
            print(f"   Brazilian options market: 09:00-17:30 BRT")
            print(f"   Open interest data shows these are real, active options")
        
    else:
        print("\n⚠️ No tradeable options found")
        print("   Check API connectivity and market hours")


if __name__ == "__main__":
    main()
