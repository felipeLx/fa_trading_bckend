#!/usr/bin/env python3
"""
Test Active Options Discovery
Compare different methods to find ACTIVE options that are currently tradeable
"""

import requests
import json
from datetime import datetime
from cedrotech_options_api import CedroTechOptionsAPI

def test_cedrotech_options_endpoints():
    """Test different CedroTech endpoints to find active options"""
    print("🔍 TESTING CEDROTECH OPTIONS ENDPOINTS")
    print("=" * 60)
    
    # Initialize API
    options_api = CedroTechOptionsAPI()
    
    if not options_api.authenticate():
        print("❌ Failed to authenticate with CedroTech")
        return
    
    # Test different underlying assets
    underlyings = ['VALE3', 'PETR4', 'ITUB4', 'BBAS3']
    
    for underlying in underlyings:
        print(f"\n📊 Testing {underlying}...")
        
        # Method 1: Current get_options_list
        print("   Method 1: get_options_list")
        result = options_api.get_options_list(underlying)
        if result.get('success'):
            options = result.get('options', [])
            print(f"      ✅ Found {len(options)} options")
            if options:
                print(f"      Sample: {options[0] if len(options) > 0 else 'None'}")
        else:
            print(f"      ❌ Failed: {result.get('error', 'Unknown error')}")
        
        # Method 2: Try direct asset info
        print("   Method 2: get_asset_info")
        asset_result = options_api.get_asset_info(underlying)
        if asset_result.get('success'):
            print(f"      ✅ Asset info received")
            data = asset_result.get('data', {})
            print(f"      Keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
        else:
            print(f"      ❌ Failed: {asset_result.get('error', 'Unknown error')}")

def test_alternative_options_sources():
    """Test alternative sources for active options data"""
    print("\n🌐 TESTING ALTERNATIVE SOURCES")
    print("=" * 60)
    
    # Test Status Invest approach (inspired by the link you shared)
    underlyings = ['VALE3', 'PETR4']
    
    for underlying in underlyings:
        print(f"\n📊 Testing {underlying} via web scraping...")
        
        try:
            # Try to get options data from public APIs
            # Note: This is for testing - we should use official APIs in production
            
            # Method 1: Try B3 official data
            print("   Method 1: B3 Official")
            b3_url = f"http://www.b3.com.br/data/files/C0/8F/28/B4/297164103F7C2E64D1774D44/HistoricalOptionsData.csv"
            # This would need proper B3 API integration
            
            # Method 2: Try Yahoo Finance (has Brazilian options)
            print("   Method 2: Yahoo Finance")
            yahoo_url = f"https://query1.finance.yahoo.com/v7/finance/options/{underlying}.SA"
            
            response = requests.get(yahoo_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                options_chain = data.get('optionChain', {})
                if options_chain:
                    print(f"      ✅ Yahoo Finance has options data for {underlying}")
                    result = options_chain.get('result', [])
                    if result:
                        options = result[0].get('options', [])
                        print(f"      Found {len(options)} option expiration dates")
                        for opt in options[:2]:  # Show first 2
                            calls = opt.get('calls', [])
                            puts = opt.get('puts', [])
                            print(f"         Calls: {len(calls)}, Puts: {len(puts)}")
                else:
                    print(f"      ⚠️ No options chain found")
            else:
                print(f"      ❌ Yahoo Finance failed: {response.status_code}")
                
        except Exception as e:
            print(f"      ❌ Error: {e}")

def test_direct_cedrotech_options_search():
    """Test direct CedroTech options search with different approaches"""
    print("\n🔧 TESTING DIRECT CEDROTECH SEARCH")
    print("=" * 60)
    
    # Initialize API
    options_api = CedroTechOptionsAPI()
    
    if not options_api.authenticate():
        print("❌ Failed to authenticate with CedroTech")
        return
    
    # Try different endpoint variations
    base_url = "https://webfeeder.cedrotech.com"
    session = options_api.session
    
    # Test different URL patterns
    test_urls = [
        f"{base_url}/services/quotes/optionsQuote/VALE3",
        f"{base_url}/services/quotes/options/VALE3",
        f"{base_url}/api/quotes/options/VALE3",
        f"{base_url}/services/market/options/VALE3",
        f"{base_url}/services/quotes/search?type=options&underlying=VALE3",
    ]
    
    for url in test_urls:
        print(f"\n🔗 Testing URL: {url}")
        try:
            response = session.get(url, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✅ JSON Response received")
                    print(f"   Type: {type(data)}")
                    
                    if isinstance(data, dict):
                        print(f"   Keys: {list(data.keys())}")
                        if 'options' in data:
                            options = data['options']
                            print(f"   📊 Found {len(options)} options in 'options' key")
                        elif isinstance(data, list):
                            print(f"   📊 Direct list with {len(data)} items")
                    
                    # Save sample for analysis
                    with open(f'cedrotech_options_sample_{datetime.now().strftime("%H%M%S")}.json', 'w') as f:
                        json.dump(data, f, indent=2)
                        
                except json.JSONDecodeError:
                    print(f"   ⚠️ Non-JSON response: {response.text[:200]}...")
            else:
                print(f"   ❌ Failed with status {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def find_active_vale_options():
    """Specifically try to find active VALE3 options like Status Invest shows"""
    print("\n🎯 SEARCHING FOR ACTIVE VALE3 OPTIONS")
    print("=" * 60)
    
    # The Status Invest link shows VALE3 options
    # Let's try to find them via different approaches
    
    print("📊 Status Invest shows these types of VALE3 options:")
    print("   - VALEH (Call options)")
    print("   - VALEF (Put options)")
    print("   - Different strike prices and expiration dates")
    
    # Try to search for specific option symbols
    options_api = CedroTechOptionsAPI()
    
    if not options_api.authenticate():
        print("❌ Failed to authenticate")
        return
      # Try searching for known VALE option patterns
    # Brazilian options typically use letter suffixes for different series
    vale_option_patterns = [
        'VALEH',  # VALE Call options (H series)
        'VALEI',  # VALE Call options (I series)
        'VALEJ',  # VALE Call options (J series)
        'VALEG',  # VALE Call options (G series)
        'VALEF',  # VALE Put options (F series)
        'VALEN',  # VALE Put options (N series)
        'VALEM',  # VALE Put options (M series)
        'VALE3H', # Alternative pattern with 3
        'VALE3F', # Alternative pattern with 3
        'VALE3I', # Alternative pattern with 3
    ]
    
    for pattern in vale_option_patterns:
        print(f"\n🔍 Searching for {pattern} options...")
        
        # Try asset info for the pattern
        result = options_api.get_asset_info(pattern)
        if result.get('success'):
            print(f"   ✅ Found asset info for {pattern}")
            data = result.get('data', {})
            print(f"   Data keys: {list(data.keys()) if isinstance(data, dict) else 'Not dict'}")        
        else:
            print(f"   ❌ No data for {pattern}")

def test_generic_options_patterns():
    """Test generic options patterns like VALEF*, PETR*, etc."""
    print("\n🎯 TESTING GENERIC OPTIONS PATTERNS")
    print("=" * 60)
    
    options_api = CedroTechOptionsAPI()
    
    if not options_api.authenticate():
        print("❌ Failed to authenticate")
        return
    
    # Brazilian options follow patterns like: VALEF480W2, VALEF490W2, PETRF50W2, etc.
    # Format: [TICKER][CALL/PUT_CODE][STRIKE][EXPIRY_CODE]
    
    # Define base patterns for major stocks
    stock_patterns = {
        'VALE3': ['VALEF', 'VALEG', 'VALEH', 'VALEI', 'VALEJ', 'VALEK'],  # VALE puts and calls
        'PETR4': ['PETRF', 'PETRG', 'PETRH', 'PETRI', 'PETRJ', 'PETRK'],  # PETROBRAS
        'ITUB4': ['ITUBF', 'ITUBG', 'ITUBH', 'ITUBI', 'ITUBJ', 'ITUBK'],  # ITAU
        'BBAS3': ['BBASF', 'BBASG', 'BBASH', 'BBASI', 'BBASJ', 'BBASK'],  # BANCO DO BRASIL
    }
    
    # Common strike price patterns (based on current stock prices)
    strike_patterns = {
        'VALE3': ['45', '46', '47', '48', '49', '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '60'],
        'PETR4': ['35', '36', '37', '38', '39', '40', '41', '42', '43', '44', '45'],
        'ITUB4': ['30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40'],
        'BBAS3': ['25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35'],
    }
    
    # Common expiry codes (W1, W2, W3, W4 for weeklies, monthly codes)
    expiry_codes = ['W1', 'W2', 'W3', 'W4', 'X1', 'X2', 'Y1', 'Y2', 'Z1', 'Z2']
    
    found_options = []
    
    for stock, patterns in stock_patterns.items():
        print(f"\n📊 Searching {stock} options...")
        
        for pattern in patterns[:3]:  # Test first 3 patterns per stock
            print(f"   🔍 Testing pattern: {pattern}*")
            
            for strike in strike_patterns[stock][:8]:  # Test first 8 strikes
                for expiry in expiry_codes[:4]:  # Test first 4 expiry codes
                    symbol = f"{pattern}{strike}{expiry}"
                    
                    result = options_api.get_asset_info(symbol)
                    if result.get('success'):
                        data = result.get('data', {})
                        bid = data.get('bid', 0)
                        ask = data.get('ask', 0)
                        
                        if bid > 0 and ask > 0:  # Active option with quotes
                            found_options.append({
                                'symbol': symbol,
                                'underlying': stock,
                                'pattern': pattern,
                                'strike': strike,
                                'expiry': expiry,
                                'bid': bid,
                                'ask': ask,
                                'spread': ((ask - bid) / ask) * 100
                            })
                            print(f"      ✅ ACTIVE: {symbol} - Bid: {bid}, Ask: {ask}")
    
    # Summary of found options
    print(f"\n🎉 SUMMARY: Found {len(found_options)} ACTIVE options!")
    if found_options:
        print("📋 Active Options List:")
        for opt in found_options[:10]:  # Show first 10
            print(f"   {opt['symbol']} ({opt['underlying']}) - Bid: {opt['bid']}, Ask: {opt['ask']}, Spread: {opt['spread']:.1f}%")
        
        # Save found options for the robot
        with open('active_options_found.json', 'w') as f:
            json.dump(found_options, f, indent=2)
        print(f"💾 Saved {len(found_options)} active options to 'active_options_found.json'")
    
    return found_options

def test_enhanced_vale_search():
    """Enhanced VALE options search with comprehensive patterns"""
    print("\n💎 ENHANCED VALE OPTIONS SEARCH")
    print("=" * 60)
    
    options_api = CedroTechOptionsAPI()
    
    if not options_api.authenticate():
        print("❌ Failed to authenticate")
        return
    
    # More comprehensive VALE patterns based on real Brazilian options
    vale_patterns = [
        'VALEF',  # VALE puts (F series)
        'VALEG',  # VALE calls (G series) 
        'VALEH',  # VALE calls (H series)
        'VALEI',  # VALE calls (I series)
        'VALEJ',  # VALE calls (J series)
        'VALEK',  # VALE calls (K series)
        'VALEL',  # VALE calls (L series)
        'VALEM',  # VALE puts (M series)
        'VALEN',  # VALE puts (N series)
        'VALEO',  # VALE puts (O series)
    ]
    
    # Strike prices around VALE3 current price (typically 45-65)
    strikes = ['42', '43', '44', '45', '46', '47', '48', '49', '50', 
               '51', '52', '53', '54', '55', '56', '57', '58', '59', '60', '61', '62', '63']
    
    # Expiry codes (weeklies and monthlies)
    expiries = ['W1', 'W2', 'W3', 'W4', 'W5', 'X1', 'X2', 'X3', 'Y1', 'Y2', 'Z1', 'Z2']
    
    vale_options = []
    
    print("🔍 Comprehensive VALE options search...")
    print(f"   Testing {len(vale_patterns)} patterns × {len(strikes)} strikes × {len(expiries)} expiries")
    print(f"   Total combinations: {len(vale_patterns) * len(strikes) * len(expiries)}")
    
    for pattern in vale_patterns:
        print(f"\n   Pattern: {pattern}*")
        pattern_found = 0
        
        for strike in strikes[:10]:  # Limit to avoid too many API calls
            for expiry in expiries[:6]:  # Test main expiry codes
                symbol = f"{pattern}{strike}{expiry}"
                
                result = options_api.get_asset_info(symbol)
                if result.get('success'):
                    data = result.get('data', {})
                    bid = data.get('bid', 0)
                    ask = data.get('ask', 0)
                    last_price = data.get('lastTrade', data.get('last', 0))
                    volume = data.get('volume', 0)
                    
                    # Consider it active if it has bid/ask or recent trading
                    if (bid > 0 and ask > 0) or last_price > 0 or volume > 0:
                        vale_options.append({
                            'symbol': symbol,
                            'pattern': pattern,
                            'strike': strike,
                            'expiry': expiry,
                            'bid': bid,
                            'ask': ask,
                            'last_price': last_price,
                            'volume': volume,
                            'spread_pct': ((ask - bid) / ask * 100) if ask > 0 else 0
                        })
                        pattern_found += 1
                        print(f"      ✅ {symbol} - Bid: {bid}, Ask: {ask}, Last: {last_price}, Vol: {volume}")
        
        print(f"   Found {pattern_found} options for pattern {pattern}")
    
    print(f"\n🎯 VALE SEARCH RESULTS:")
    print(f"   Total VALE options found: {len(vale_options)}")
    
    if vale_options:
        # Sort by volume and spread quality
        sorted_options = sorted(vale_options, key=lambda x: (x['volume'], -x['spread_pct']), reverse=True)
        
        print("\n🏆 Top 10 VALE options by volume and spread:")
        for i, opt in enumerate(sorted_options[:10]):
            print(f"   {i+1}. {opt['symbol']} - Bid: {opt['bid']}, Ask: {opt['ask']}, Vol: {opt['volume']}, Spread: {opt['spread_pct']:.1f}%")
        
        # Save VALE options
        with open('active_vale_options.json', 'w') as f:
            json.dump(sorted_options, f, indent=2)
        print(f"💾 Saved {len(sorted_options)} VALE options to 'active_vale_options.json'")
    
    return vale_options

def test_b3_options_search():
    """Try to find options using B3 (Brazilian Exchange) patterns"""
    print("\n🇧🇷 TESTING B3 OPTIONS PATTERNS")
    print("=" * 60)
    
    options_api = CedroTechOptionsAPI()
    
    if not options_api.authenticate():
        print("❌ Failed to authenticate")
        return
    
    # Test some known option symbols from Status Invest pattern
    known_patterns = [
        'VALEF480W2', 'VALEF490W2', 'VALEF500W2',  # VALE puts
        'VALEG480W2', 'VALEG490W2', 'VALEG500W2',  # VALE calls
        'PETRF40W2', 'PETRF42W2', 'PETRF45W2',     # PETROBRAS
    ]
    
    print("🔍 Testing known option patterns...")
    for symbol in known_patterns:
        result = options_api.get_asset_info(symbol)
        if result.get('success'):
            data = result.get('data', {})
            print(f"   ✅ FOUND: {symbol}")
            print(f"      Bid: {data.get('bid', 0)}, Ask: {data.get('ask', 0)}")
            print(f"      Last: {data.get('lastTrade', 0)}, Volume: {data.get('volume', 0)}")
        else:
            print(f"   ❌ Not found: {symbol}")

if __name__ == "__main__":
    print("🚀 ACTIVE OPTIONS DISCOVERY TEST")
    print("=" * 80)
    
    # Test 1: CedroTech endpoints
    test_cedrotech_options_endpoints()
    
    # Test 2: Alternative sources
    test_alternative_options_sources()
    
    # Test 3: Direct CedroTech search
    test_direct_cedrotech_options_search()
    
    # Test 4: Specific VALE search
    find_active_vale_options()
    
    # Test 5: Generic options patterns (COMPREHENSIVE)
    test_generic_options_patterns()
    
    # Test 6: Enhanced VALE search (WILDCARD PATTERNS)
    test_enhanced_vale_search()
    
    # Test 7: B3 options patterns
    test_b3_options_search()
    
    print("\n" + "=" * 80)
    print("✅ TESTING COMPLETE")
    print("📋 Summary:")
    print("   - Check 'active_options_found.json' for all found options")
    print("   - Check 'active_vale_options.json' for VALE-specific options")
    print("   - Look for ✅ ACTIVE or ✅ FOUND entries in the output above")
    print("   - These are the options that can be traded RIGHT NOW!")
