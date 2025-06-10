#!/usr/bin/env python3
"""
Live Options Quote Testing Script
Test the options robot during market hours to validate real-time bid/ask quotes
Run this script during Brazilian market hours (9:00-17:30) to validate options data
"""

import time
from datetime import datetime
from cedrotech_options_api import CedroTechOptionsAPI
from options_robot import validate_option_tradeable, TRADEABLE_OPTIONS, is_market_hours

def test_live_options_quotes():
    """Test real-time options quotes during market hours"""
    print("🎯 LIVE OPTIONS QUOTE TESTING")
    print("=" * 60)
    
    # Check if market is open
    if not is_market_hours():
        current_time = datetime.now().strftime("%H:%M")
        print(f"⚠️ Market is closed ({current_time})")
        print("📅 Brazilian market hours: 09:00 - 17:30")
        print("⏰ Run this script during market hours for live testing")
        return False
    
    print(f"✅ Market is open - starting live quote test")
    print(f"🕒 Test time: {datetime.now().strftime('%H:%M:%S')}")
    
    try:
        # Initialize options API
        options_api = CedroTechOptionsAPI()
        print("✅ Options API initialized successfully")
        
        # Test each target option
        tradeable_found = False
        
        for i, option_info in enumerate(TRADEABLE_OPTIONS, 1):
            symbol = option_info['symbol']
            expected_score = option_info['score']
            underlying = option_info['underlying']
            
            print(f"\n🔍 Testing Option {i}/2: {symbol}")
            print(f"   Underlying: {underlying}")
            print(f"   Expected Score: {expected_score}/100")
            print(f"   Expected Open Interest: {option_info['open_interest']:,}")
            
            # Validate option
            validation = validate_option_tradeable(symbol, options_api)
            
            if validation['tradeable']:
                print("✅ OPTION IS TRADEABLE!")
                print(f"   💰 Bid: R${validation['bid']:.2f}")
                print(f"   💰 Ask: R${validation['ask']:.2f}")
                print(f"   📊 Last Trade: R${validation['last_trade']:.2f}")
                print(f"   📈 Volume: {validation['volume']:,}")
                print(f"   📊 Open Interest: {validation['open_interest']:,}")
                print(f"   📏 Bid/Ask Spread: {validation['spread_percent']:.1f}%")
                
                # Detailed validation checks
                checks = validation['checks']
                print(f"   ✅ Validation Summary:")
                for check_name, passed in checks.items():
                    status = "✅" if passed else "❌"
                    print(f"      {status} {check_name.replace('_', ' ').title()}")
                
                tradeable_found = True
                  # Real-time monitoring test (30 seconds)
                print(f"\n📡 Real-time monitoring test for {symbol} (30 seconds)...")
                for tick in range(6):  # 6 ticks, 5 seconds apart
                    time.sleep(5)
                    current_quote_result = options_api.get_asset_info(symbol)
                    if current_quote_result and current_quote_result.get('success'):
                        current_quote = current_quote_result.get('data', {})
                        bid = float(current_quote.get('bid', current_quote.get('bidPrice', 0)))
                        ask = float(current_quote.get('ask', current_quote.get('askPrice', 0)))
                        print(f"   Tick {tick+1}: Bid={bid:.2f}, Ask={ask:.2f}")
                    else:
                        print(f"   Tick {tick+1}: No quote available")
                        
            else:
                print("❌ OPTION NOT TRADEABLE")
                print(f"   🚫 Reason: {validation['reason']}")
                print(f"   📊 Bid: {validation.get('bid', 0):.2f}")
                print(f"   📊 Ask: {validation.get('ask', 0):.2f}")
                print(f"   📊 Volume: {validation.get('volume', 0)}")
                print(f"   📊 Open Interest: {validation.get('open_interest', 0)}")
        
        return tradeable_found
        
    except Exception as e:
        print(f"❌ Error during live testing: {e}")
        return False

def test_market_hours_check():
    """Test market hours detection"""
    print("\n🕐 MARKET HOURS TESTING")
    print("=" * 40)
    
    current_time = datetime.now()
    print(f"Current time: {current_time.strftime('%H:%M:%S')}")
    print(f"Current date: {current_time.strftime('%Y-%m-%d')}")
    print(f"Weekday: {current_time.strftime('%A')}")
    
    is_open = is_market_hours()
    print(f"Market status: {'OPEN' if is_open else 'CLOSED'}")
    
    if is_open:
        print("✅ Perfect time for options testing!")
    else:
        print("⏰ Market closed - wait for trading hours")
        print("📅 Brazilian B3 hours: Monday-Friday 09:00-17:30")

def comprehensive_options_test():
    """Run comprehensive options testing suite"""
    print("🚀 COMPREHENSIVE OPTIONS TESTING SUITE")
    print("=" * 70)
    
    # 1. Market hours check
    test_market_hours_check()
    
    # 2. Live quotes test (only if market is open)
    if is_market_hours():
        print("\n" + "=" * 50)
        tradeable_found = test_live_options_quotes()
        
        if tradeable_found:
            print("\n🎉 SUCCESS: At least one option is tradeable!")
            print("✅ Your options robot is ready for live testing")
            print("\n📋 NEXT STEPS:")
            print("1. Run: python options_robot.py")
            print("2. Monitor for 30 minutes during market hours")
            print("3. Validate bid/ask quotes are updating")
            print("4. Test small position sizing")
        else:
            print("\n⚠️ WARNING: No options are currently tradeable")
            print("🔧 TROUBLESHOOTING:")
            print("1. Check if B3 market is actually open")
            print("2. Verify VALE3 options are actively traded today")
            print("3. Try testing again in 15 minutes")
            print("4. Consider expanding target options list")
    else:
        print("\n⏳ Market is closed - cannot test live quotes")
        print("📅 Come back during trading hours: 09:00-17:30 BRT")

if __name__ == "__main__":
    try:
        comprehensive_options_test()
    except KeyboardInterrupt:
        print("\n🛑 Testing stopped by user")
    except Exception as e:
        print(f"\n❌ Testing error: {e}")
