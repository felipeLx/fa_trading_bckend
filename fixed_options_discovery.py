#!/usr/bin/env python3
"""
Fixed Options Discovery - Using Correct CedroTech API
Gets REAL active options from the API instead of guessing codes
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from cedrotech_options_api import CedroTechOptionsAPI
from options_filter_analysis import OptionsTradeabilityAnalyzer

class FixedOptionsDiscovery:
    """
    Fixed options discovery that uses the correct CedroTech API endpoints
    1. Gets actual options list from /services/quotes/optionsQuote/{underlying}
    2. Validates each option from the returned list
    3. Applies quality analysis only to REAL options
    """
    def __init__(self):
        self.options_api = CedroTechOptionsAPI()
        self.analyzer = OptionsTradeabilityAnalyzer()
        
        # Major Ibovespa underlyings to check (expanded list)
        self.underlyings = [
            'VALE3', 'PETR4', 'ITUB4', 'BBAS3', 'B3SA3',  # Original
            'ABEV3', 'MGLU3', 'WEGE3', 'RENT3', 'LREN3',  # Large caps
            'JBSS3', 'BEEF3', 'SUZB3', 'GOAU4', 'USIM5'   # More options
        ]
        
        # Test specific option symbols that might exist
        self.test_option_symbols = [
            'VALEF', 'VALEG', 'VALEH', 'VALEI', 'VALEJ',   # VALE options
            'PETRF', 'PETRG', 'PETRH', 'PETRI', 'PETRJ',   # PETR options
            'ITUBF', 'ITUBG', 'ITUBH', 'ITUBL', 'ITUBM',   # ITUB options
            'BBASF', 'BBASG', 'BBASH', 'BBASI', 'BBASJ'    # BBAS options
        ]
          def discover_real_options(self) -> Dict[str, List[Dict]]:
        """
        Discover REAL active options using the working companyQuotes endpoint
        Returns only options that actually exist and have data
        """
        print("🔍 FIXED OPTIONS DISCOVERY - USING COMPANY QUOTES ENDPOINT")
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
                        for symbol in options_symbols[:50]:  # Process first 50 options
                            option_data = self._get_option_quote(symbol, underlying)
                            if option_data:
                                real_options.append(option_data)
                        
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
            return []
    
    def _get_option_quote(self, symbol: str, underlying: str) -> Optional[Dict]:
        """Get detailed quote for a specific option symbol"""
        try:
            # Use the asset info endpoint to get option details
            result = self.options_api.get_asset_info(symbol)
            
            if result.get('success'):
                data = result.get('data', {})
                
                # Extract option data with fallbacks
                bid = float(data.get('bid', 0) or 0)
                ask = float(data.get('ask', 0) or 0)
                last_trade = float(data.get('lastTrade', 0) or data.get('last', 0) or 0)
                volume = int(data.get('volume', 0) or 0)
                open_interest = int(data.get('openInterest', 0) or data.get('interest', 0) or 0)
                
                # Only include options with some activity
                if bid > 0 or ask > 0 or last_trade > 0 or open_interest > 0:
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
            
            return None
            
        except Exception as e:
            # Don't print error for each failed option (too noisy)
            return None
    
    def _process_options_list(self, underlying: str, options_list: List) -> List[Dict]:
        """Process options data when it's returned as a list"""
        real_options = []
        
        for option_data in options_list:
            if isinstance(option_data, dict):
                processed_option = self._extract_option_data(underlying, option_data)
                if processed_option:
                    real_options.append(processed_option)
        
        return real_options
    
    def _process_options_dict(self, underlying: str, options_dict: Dict) -> List[Dict]:
        """Process options data when it's returned as a dict"""
        real_options = []
        
        # Look for common keys that might contain options arrays
        possible_keys = ['options', 'data', 'result', 'calls', 'puts']
        
        for key in possible_keys:
            if key in options_dict and isinstance(options_dict[key], list):
                print(f"   📋 Found options in '{key}' field")
                for option_data in options_dict[key]:
                    processed_option = self._extract_option_data(underlying, option_data)
                    if processed_option:
                        real_options.append(processed_option)
        
        # If no arrays found, try to process the dict itself as an option
        if not real_options:
            processed_option = self._extract_option_data(underlying, options_dict)
            if processed_option:
                real_options.append(processed_option)
        
        return real_options
    
    def _extract_option_data(self, underlying: str, option_data: Dict) -> Optional[Dict]:
        """Extract and standardize option data from API response"""
        try:
            # Try to extract option symbol (different possible field names)
            symbol = (option_data.get('symbol') or 
                     option_data.get('code') or 
                     option_data.get('ticker') or 
                     option_data.get('optionCode') or
                     option_data.get('codAtivo'))
            
            if not symbol:
                return None
            
            # Extract financial data with multiple possible field names
            bid = float(option_data.get('bid', 0) or 
                       option_data.get('bidPrice', 0) or 
                       option_data.get('precoCompra', 0))
            
            ask = float(option_data.get('ask', 0) or 
                       option_data.get('askPrice', 0) or 
                       option_data.get('precoVenda', 0))
            
            last_trade = float(option_data.get('lastTrade', 0) or 
                              option_data.get('last', 0) or 
                              option_data.get('price', 0) or 
                              option_data.get('ultimoNegocio', 0))
            
            volume = int(option_data.get('volume', 0) or 
                        option_data.get('volumeAmount', 0) or 
                        option_data.get('quantidade', 0))
            
            open_interest = int(option_data.get('openInterest', 0) or 
                               option_data.get('interest', 0) or 
                               option_data.get('posicaoAberta', 0))
            
            # Only include options with some trading activity
            if (bid > 0 or ask > 0 or last_trade > 0 or 
                volume > 0 or open_interest > 0):
                
                return {
                    'symbol': symbol,
                    'underlying': underlying,
                    'bid': bid,
                    'ask': ask,
                    'last_trade': last_trade,
                    'volume': volume,
                    'open_interest': open_interest,
                    'discovery_time': datetime.now().isoformat(),
                    'raw_data': option_data  # Keep original data for debugging
                }
            
            return None
            
        except Exception as e:
            print(f"   ⚠️ Error processing option data: {e}")
            return None
    
    def validate_real_options(self, discovered_options: Dict) -> Dict:
        """
        Validate the discovered options using individual API calls
        Only call API for options we know exist
        """
        print("\n📊 VALIDATING REAL OPTIONS...")
        print("=" * 60)
        
        validated_options = {}
        total_validated = 0
        
        for underlying, data in discovered_options.items():
            print(f"\n🔍 Validating {underlying} options...")
            
            underlying_options = []
            options_list = data.get('options', [])
            
            for option in options_list[:10]:  # Limit to avoid too many API calls
                symbol = option['symbol']
                print(f"   📊 Validating {symbol}...")
                
                # Get detailed quote for this specific option
                quote_result = self.options_api.get_asset_info(symbol)
                
                if quote_result.get('success'):
                    quote_data = quote_result.get('data', {})
                    
                    # Update option with detailed quote data
                    enhanced_option = option.copy()
                    enhanced_option.update({
                        'bid': float(quote_data.get('bid', option['bid'])),
                        'ask': float(quote_data.get('ask', option['ask'])),
                        'last_trade': float(quote_data.get('lastTrade', quote_data.get('last', option['last_trade']))),
                        'volume': int(quote_data.get('volume', option['volume'])),
                        'open_interest': int(quote_data.get('openInterest', option['open_interest'])),
                        'validation_time': datetime.now().isoformat()
                    })
                    
                    underlying_options.append(enhanced_option)
                    total_validated += 1
                    
                    print(f"      ✅ VALIDATED: Bid: {enhanced_option['bid']:.2f}, Ask: {enhanced_option['ask']:.2f}, OI: {enhanced_option['open_interest']:,}")
                else:
                    print(f"      ❌ Validation failed: {quote_result.get('error', 'Unknown error')}")
            
            if underlying_options:
                validated_options[underlying] = {'options': underlying_options}
                print(f"   📈 {len(underlying_options)} options validated for {underlying}")
        
        print(f"\n✅ VALIDATION SUMMARY:")
        print(f"   Total validated options: {total_validated}")
        
        return validated_options
    
    def get_daily_tradeable_options(self, max_options: int = 15) -> List[Dict]:
        """
        Main method: Get today's REAL tradeable options
        
        Returns:
            List of validated, real options in robot format
        """
        print("🚀 GETTING REAL DAILY TRADEABLE OPTIONS")
        print("=" * 80)
        
        # Step 1: Discover real options from API
        discovered = self.discover_real_options()
        if not discovered:
            print("❌ No real options discovered from API")
            return []
        
        # Step 2: Validate options with individual calls (but only for options we know exist)
        validated = self.validate_real_options(discovered)
        if not validated:
            print("❌ No options validated")
            return []
        
        # Step 3: Apply quality analysis
        print("\n📊 APPLYING QUALITY ANALYSIS...")
        analyzed = self.analyzer.filter_tradeable_options(validated)
        
        if not analyzed.get('tradeable_options'):
            print("❌ No tradeable options after quality analysis")
            return []
        
        # Step 4: Convert to robot format
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
                'is_real_option': True  # Flag to indicate this is a real option from API
            }
            
            robot_options.append(robot_option)
        
        # Step 5: Print summary
        print(f"\n🎯 REAL OPTIONS READY FOR ROBOT:")
        print(f"   Found {len(robot_options)} REAL tradeable options")
        
        if robot_options:
            print("\n🏆 Top 5 REAL options:")
            for i, opt in enumerate(robot_options[:5]):
                print(f"   {i+1}. {opt['symbol']} ({opt['underlying']}) - Score: {opt['score']}/100, Rating: {opt['rating']}")
                print(f"      OI: {opt['open_interest']:,} | Vol: {opt['volume']} | Spread: {opt['spread_pct']:.1f}%")
        
        # Step 6: Save results
        with open('real_options_discovery.json', 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'discovered_count': sum(len(v['options']) for v in discovered.values()),
                'validated_count': sum(len(v['options']) for v in validated.values()),
                'robot_options': robot_options
            }, f, indent=2)
        
        print(f"\n💾 Results saved to: real_options_discovery.json")
        
        return robot_options

    def debug_api_response(self, underlying: str) -> None:
        """Debug the actual API response structure"""
        print(f"\n🔍 DEBUGGING API RESPONSE FOR {underlying}")
        print("=" * 50)
        
        options_result = self.options_api.get_options_list(underlying)
        
        if options_result.get('success'):
            options_data = options_result.get('options')
            print(f"   📊 Response Type: {type(options_data)}")
            
            if isinstance(options_data, dict):
                print(f"   📋 Dictionary Keys: {list(options_data.keys())}")
                for key, value in options_data.items():
                    print(f"      {key}: {type(value)} - {len(value) if isinstance(value, (list, dict)) else str(value)[:50]}")
            elif isinstance(options_data, list):
                print(f"   📋 List Length: {len(options_data)}")
                if options_data:
                    print(f"   📋 First Item Type: {type(options_data[0])}")
                    if isinstance(options_data[0], dict):
                        print(f"   📋 First Item Keys: {list(options_data[0].keys())}")
            else:
                print(f"   📋 Raw Data: {str(options_data)[:200]}")
        else:
            print(f"   ❌ API Error: {options_result.get('error')}")
    
    def test_individual_option_symbols(self) -> Dict[str, Dict]:
        """Test individual option symbols to see if they exist"""
        print("\n🎯 TESTING INDIVIDUAL OPTION SYMBOLS")
        print("=" * 60)
        
        found_options = {}
        
        for symbol in self.test_option_symbols[:10]:  # Test first 10
            print(f"\n📊 Testing option symbol: {symbol}")
            
            # Test get_asset_info for this specific symbol
            result = self.options_api.get_asset_info(symbol)
            
            if result.get('success'):
                data = result.get('data', {})
                print(f"   ✅ Symbol {symbol} EXISTS!")
                print(f"   💰 Data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                
                # Extract key data
                if isinstance(data, dict):
                    bid = data.get('bid', 0)
                    ask = data.get('ask', 0)
                    last = data.get('lastTrade', data.get('last', 0))
                    volume = data.get('volume', 0)
                    oi = data.get('openInterest', data.get('interest', 0))
                    
                    print(f"   💲 Bid: {bid}, Ask: {ask}, Last: {last}")
                    print(f"   📊 Volume: {volume}, OI: {oi}")
                    
                    if bid > 0 or ask > 0 or last > 0:
                        found_options[symbol] = {
                            'symbol': symbol,
                            'bid': float(bid),
                            'ask': float(ask),
                            'last': float(last),
                            'volume': int(volume),
                            'open_interest': int(oi),
                            'raw_data': data
                        }
                        print(f"   🎯 ACTIVE OPTION FOUND!")
            else:
                error = result.get('error', 'Unknown error')
                if '404' in error:
                    print(f"   ❌ Symbol {symbol} does not exist (404)")
                else:
                    print(f"   ❌ Error: {error}")
        
        print(f"\n📈 INDIVIDUAL SYMBOL TEST RESULTS:")
        print(f"   Found {len(found_options)} active option symbols")
        
        if found_options:
            print("   🏆 Active options found:")
            for symbol, data in found_options.items():
                print(f"      {symbol}: Bid={data['bid']:.2f}, Ask={data['ask']:.2f}, Vol={data['volume']}")
        
        return found_options

def main():
    """Test the fixed discovery system with extensive debugging"""
    print("🔧 TESTING FIXED OPTIONS DISCOVERY WITH DEBUGGING")
    print("=" * 80)
    
    discovery = FixedOptionsDiscovery()
    
    # Test 1: Debug API response structure
    print("\n🔍 STEP 1: DEBUG API RESPONSE STRUCTURE")
    for underlying in ['VALE3', 'PETR4', 'ITUB4'][:2]:  # Test first 2
        discovery.debug_api_response(underlying)
    
    # Test 2: Test individual option symbols
    print("\n🎯 STEP 2: TEST INDIVIDUAL OPTION SYMBOLS")
    found_individual = discovery.test_individual_option_symbols()
    
    # Test 3: Try full discovery process
    print("\n🚀 STEP 3: FULL DISCOVERY PROCESS")
    options = discovery.get_daily_tradeable_options(max_options=20)
    
    # Summary
    print("\n📊 COMPREHENSIVE TEST SUMMARY")
    print("=" * 60)
    
    if found_individual:
        print(f"✅ Individual symbol test: Found {len(found_individual)} active options")
        print("   🎯 This proves options exist and can be accessed!")
        
        # Show which symbols work
        print("   🏆 Working option symbols:")
        for symbol in found_individual.keys():
            print(f"      • {symbol}")
            
    if options:
        print(f"✅ Full discovery: Found {len(options)} tradeable options")
        print("🚀 Ready for robot integration!")
    else:
        print("⚠️ Full discovery: No options found")
        
        if found_individual:
            print("💡 SOLUTION: Individual symbols work, but underlying discovery doesn't")
            print("   → We should modify the robot to use direct symbol lookup")
        else:
            print("💡 ANALYSIS NEEDED:")
            print("   - Check if market is open")
            print("   - Verify option symbol patterns")
            print("   - Test with different underlyings")

if __name__ == "__main__":
    main()
