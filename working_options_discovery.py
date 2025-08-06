#!/usr/bin/env python3
"""
Working Options Discovery - Using Company Quotes Endpoint
Uses the WORKING /services/quotes/companyQuotes endpoint that returns real options
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from cedrotech_options_api import CedroTechOptionsAPI
from options_filter_analysis import OptionsTradeabilityAnalyzer

class WorkingOptionsDiscovery:
    """
    Working options discovery using the companyQuotes endpoint
    This endpoint actually returns 814 active VALE options!
    """
    
    def __init__(self):
        self.options_api = CedroTechOptionsAPI()
        self.analyzer = OptionsTradeabilityAnalyzer()
        
        # Major Ibovespa underlyings to check
        self.underlyings = [
            'VALE3', 'PETR4', 'ITUB4', 'BBAS3', 'B3SA3',  # Original
            'ABEV3', 'MGLU3', 'WEGE3', 'RENT3', 'LREN3'   # Large caps
        ]
        
    def discover_real_options(self) -> Dict[str, List[Dict]]:
        """
        Discover REAL active options using the working companyQuotes endpoint
        Returns only options that actually exist and have data
        """
        print("🔍 WORKING OPTIONS DISCOVERY - USING COMPANY QUOTES ENDPOINT")
        print("=" * 70)
        
        if not self.options_api.authenticate():
            print("❌ Failed to authenticate with CedroTech API")
            return {}
        
        discovered_options = {}
        total_real_options = 0
        
        # Company name mapping for the API
        company_mapping = {
            'VALE3': 'VALE',
            'PETR4': 'PETROBRAS', 
            'ITUB4': 'ITAU',
            'BBAS3': 'BRADESCO',
            'B3SA3': 'B3',
            'ABEV3': 'AMBEV',
            'MGLU3': 'MAGALU',
            'WEGE3': 'WEG',
            'RENT3': 'LOCALIZA',
            'LREN3': 'LOJAS_RENNER'
        }
        
        for underlying in self.underlyings:
            company_name = company_mapping.get(underlying, underlying.replace('3', '').replace('4', ''))
            print(f"\n📊 Getting REAL options for {underlying} (company: {company_name})...")
            
            # Use the WORKING companyQuotes endpoint
            real_options = self._get_company_options(company_name, underlying)
            
            if real_options:
                discovered_options[underlying] = {'options': real_options}
                total_real_options += len(real_options)
                print(f"   ✅ Found {len(real_options)} REAL options for {underlying}")
                
                # Show sample of real options found
                for i, opt in enumerate(real_options[:3]):  # Show first 3
                    print(f"      {i+1}. {opt['symbol']} - Bid: {opt.get('bid', 0):.2f}, Ask: {opt.get('ask', 0):.2f}")
            else:
                print(f"   ⚠️ No options found for {underlying}")
        
        print(f"\n🎯 DISCOVERY SUMMARY:")
        print(f"   Total REAL options found: {total_real_options}")
        print(f"   Underlyings with options: {len(discovered_options)}")
        
        return discovered_options
    
    def _get_company_options(self, company_name: str, underlying: str) -> List[Dict]:
        """Get options for a company using the working companyQuotes endpoint"""
        try:
            # Use the session from authenticated API
            session = self.options_api.session
            base_url = self.options_api.base_url
            
            # Company quotes endpoint - this WORKS!
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
                    options_symbols = response.json()
                    
                    if isinstance(options_symbols, list) and options_symbols:
                        print(f"   📋 Found {len(options_symbols)} option symbols from API")
                          # Now get detailed data for each option (limit to avoid overload)
                        real_options = []
                        debug_count = 0  # Only debug first few options
                        for i, symbol in enumerate(options_symbols[:50]):  # Process first 50 options
                            option_data = self._get_option_quote(symbol, underlying, debug=(debug_count < 3))
                            if option_data:
                                real_options.append(option_data)
                            debug_count += 1
                            
                            # Show progress every 10 options
                            if (i + 1) % 10 == 0:
                                print(f"      📊 Processed {i + 1}/{min(50, len(options_symbols))} options...")
                        
                        print(f"   💰 Successfully got data for {len(real_options)} options")
                        return real_options
                    else:
                        print(f"   ⚠️ No options returned in list format")
                        return []
                        
                except json.JSONDecodeError:
                    print(f"   ❌ Invalid JSON response")
                    return []
            else:
                print(f"   ❌ Company quotes failed: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"   💥 Error getting company options: {e}")
            return []    def _get_option_quote(self, symbol: str, underlying: str, debug: bool = False) -> Optional[Dict]:
        """Get detailed quote for a specific option symbol"""
        try:
            # Use the asset info endpoint to get option details
            result = self.options_api.get_asset_info(symbol)
            
            if result.get('success'):
                data = result.get('data', {})
                
                # DEBUG: Print the actual data structure we're getting
                print(f"      🔍 DEBUG - Raw data for {symbol}:")
                print(f"         Keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                if isinstance(data, dict) and data:
                    # Show first few key-value pairs
                    sample_data = {k: v for i, (k, v) in enumerate(data.items()) if i < 5}
                    print(f"         Sample data: {sample_data}")
                
                # Extract option data with fallbacks - try multiple possible field names
                bid = float(data.get('bid', 0) or data.get('bidPrice', 0) or data.get('currentBid', 0) or 0)
                ask = float(data.get('ask', 0) or data.get('askPrice', 0) or data.get('currentAsk', 0) or 0)
                last_trade = float(data.get('lastTrade', 0) or data.get('last', 0) or data.get('lastPrice', 0) or data.get('price', 0) or 0)
                volume = int(data.get('volume', 0) or data.get('dailyVolume', 0) or data.get('tradedVolume', 0) or 0)
                open_interest = int(data.get('openInterest', 0) or data.get('interest', 0) or data.get('oi', 0) or 0)                
                # Only include options with some activity
                if bid > 0 or ask > 0 or last_trade > 0 or open_interest > 0:
                    print(f"         ✅ VALID OPTION: bid={bid}, ask={ask}, last={last_trade}, vol={volume}, oi={open_interest}")
                    return {
                        'symbol': symbol,
                        'underlying': underlying,
                        'bid': bid,
                        'ask': ask,
                        'last_trade': last_trade,
                        'volume': volume,
                        'open_interest': open_interest,
                        'discovery_time': datetime.now().isoformat(),
                        'raw_data': data
                    }
                else:
                    print(f"         ❌ NO ACTIVITY: bid={bid}, ask={ask}, last={last_trade}, vol={volume}, oi={open_interest}")
            
            return None
            
        except Exception as e:
            # Don't print error for each failed option (too noisy)
            return None
    
    def get_daily_tradeable_options(self, max_options: int = 15) -> List[Dict]:
        """
        Main method: Get today's REAL tradeable options using working endpoint
        
        Returns:
            List of validated, real options in robot format
        """
        print("🚀 GETTING REAL DAILY TRADEABLE OPTIONS")
        print("=" * 80)
        
        # Step 1: Discover real options from working API
        discovered = self.discover_real_options()
        if not discovered:
            print("❌ No real options discovered from API")
            return []
        
        # Step 2: Apply quality analysis
        print("\n📊 APPLYING QUALITY ANALYSIS...")
        analyzed = self.analyzer.filter_tradeable_options(discovered)
        
        if not analyzed.get('tradeable_options'):
            print("❌ No tradeable options after quality analysis")
            return []
        
        # Step 3: Convert to robot format
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
                'discovery_timestamp': datetime.now().isoformat(),
                'strengths': option['strengths'],
                'warnings': option['warnings'],
                'is_real_option': True,  # Flag to indicate this is a real option from API
                'discovery_method': 'companyQuotes'  # Track which method found this
            }
            
            robot_options.append(robot_option)
        
        # Step 4: Print summary
        print(f"\n🎯 REAL OPTIONS READY FOR ROBOT:")
        print(f"   Found {len(robot_options)} REAL tradeable options")
        
        if robot_options:
            print("\n🏆 Top 5 REAL options:")
            for i, opt in enumerate(robot_options[:5]):
                print(f"   {i+1}. {opt['symbol']} ({opt['underlying']}) - Score: {opt['score']}/100, Rating: {opt['rating']}")
                print(f"      OI: {opt['open_interest']:,} | Vol: {opt['volume']} | Spread: {opt['spread_pct']:.1f}%")
        
        # Step 5: Save results
        with open('working_options_discovery.json', 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'discovery_method': 'companyQuotes',
                'discovered_count': sum(len(v['options']) for v in discovered.values()),
                'robot_options': robot_options
            }, f, indent=2)
        
        print(f"\n💾 Results saved to: working_options_discovery.json")
        
        return robot_options

def main():
    """Test the working discovery system"""
    print("🔧 TESTING WORKING OPTIONS DISCOVERY")
    print("=" * 80)
    
    discovery = WorkingOptionsDiscovery()
    options = discovery.get_daily_tradeable_options(max_options=20)
    
    if options:
        print(f"\n✅ SUCCESS: Found {len(options)} REAL tradeable options!")
        print("🚀 These are actual options from CedroTech API")
        print("🎯 Ready for integration with options_robot.py")
        
        # Show breakdown by underlying
        by_underlying = {}
        for opt in options:
            underlying = opt['underlying']
            if underlying not in by_underlying:
                by_underlying[underlying] = []
            by_underlying[underlying].append(opt)
        
        print(f"\n📊 Options by underlying:")
        for underlying, opts in by_underlying.items():
            print(f"   {underlying}: {len(opts)} options")
    else:
        print("\n⚠️ No real options found")
        print("   This could mean:")
        print("   - Market might be closed")
        print("   - Quality filters too strict")
        print("   - API rate limiting")

if __name__ == "__main__":
    main()
