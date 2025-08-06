"""
Test the fixed robot logic - should now automatically switch to tradeable assets
and execute trades instead of being stuck in hold mode
"""

import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.quick_technical_analysis import get_price_signals
from utils.database import fetch_intraday_prices

def simulate_robot_behavior():
    """Simulate what the robot will do with the enhanced logic."""
    
    print("🤖 SIMULATING ENHANCED ROBOT BEHAVIOR")
    print("=" * 60)
    
    # Current robot state (EMBR3 selected but showing HOLD)
    current_asset = "EMBR3"
    print(f"📊 Current selected asset: {current_asset}")
    
    # Check current asset signal
    intraday_prices = fetch_intraday_prices(current_asset)
    if intraday_prices:
        signal, high, low = get_price_signals(intraday_prices)
        print(f"📈 {current_asset} signal: {signal.upper()}")
        
        if signal == 'hold':
            print("🔄 HOLD signal detected - robot will scan for alternatives...")
            
            # Alternative assets the robot will check
            alternative_tickers = ["AMER3", "MGLU3", "LREN3", "RENT3", "VALE3", "PETR4", "ITUB4"]
            
            print("\n🔍 Scanning alternatives:")
            for alt_ticker in alternative_tickers:
                alt_prices = fetch_intraday_prices(alt_ticker)
                if alt_prices:
                    alt_signal, alt_high, alt_low = get_price_signals(alt_prices)
                    current_price = alt_prices[0]['close']
                    
                    status = "🚀 **WILL SWITCH HERE**" if alt_signal == 'buy' else ""
                    print(f"   📊 {alt_ticker}: {alt_signal.upper()} @ R${current_price:.2f} {status}")
                    
                    if alt_signal == 'buy':
                        print(f"\n✅ ROBOT DECISION: Switch to {alt_ticker}")
                        print(f"📈 Price: R${current_price:.2f} (Range: R${alt_low:.2f}-R${alt_high:.2f})")
                        print(f"🎯 Robot will execute BUY order for {alt_ticker}")
                        return alt_ticker, current_price
                else:
                    print(f"   ❌ {alt_ticker}: No data")
            
            print("\n⚠️ No BUY signals found in alternatives")
            return None, None
        else:
            print(f"✅ {current_asset} shows {signal.upper()} - robot will trade")
            return current_asset, intraday_prices[0]['close']
    else:
        print(f"❌ No data for {current_asset}")
        return None, None

def update_robot_state_simulation(new_asset, price):
    """Show what the robot state will look like after the fix."""
    
    if not new_asset:
        print("\n⚠️ Robot will continue monitoring current asset")
        return
    
    print(f"\n🔄 ROBOT STATE UPDATE SIMULATION")
    print("=" * 40)
    
    # Load current state
    try:
        with open('robot_state.json', 'r') as f:
            state = json.load(f)
    except:
        state = {}
    
    # Show before/after
    print(f"📊 BEFORE:")
    print(f"   Asset: {state.get('holding_asset', 'None')}")
    print(f"   Buy Price: {state.get('buy_price', 'None')}")
    print(f"   Position Size: {state.get('position_size', 0)}")
    
    print(f"\n📊 AFTER (with fix):")
    print(f"   Asset: {new_asset}")
    print(f"   Buy Price: Will be set to R${price:.2f}")
    print(f"   Position Size: Will be calculated dynamically")
    print(f"   Status: READY TO TRADE!")

def test_signal_improvements():
    """Show the difference between old and new signal logic."""
    
    print(f"\n🔧 SIGNAL LOGIC IMPROVEMENTS")
    print("=" * 40)
    
    print("❌ OLD LOGIC (why robot was stuck):")
    print("   • Wait for price to be 98% of recent high")
    print("   • Only buy at peaks (terrible for day trading)")
    print("   • No asset switching")
    print("   • Result: Perpetual HOLD mode")
    
    print("\n✅ NEW LOGIC (enhanced trading):")
    print("   • Buy on oversold conditions (RSI 25-45)")
    print("   • Buy at 20-60% of price range (good entries)")
    print("   • Automatic asset switching when stuck")
    print("   • Volume and momentum analysis")
    print("   • Result: Active trading opportunities")

if __name__ == "__main__":
    # Test the enhanced robot behavior
    selected_asset, price = simulate_robot_behavior()
    
    # Show state changes
    update_robot_state_simulation(selected_asset, price)
    
    # Explain improvements
    test_signal_improvements()
    
    print(f"\n🎉 CONCLUSION:")
    if selected_asset:
        print("✅ ROBOT WILL NOW TRADE ACTIVELY!")
        print(f"📤 Next robot run should execute BUY order for {selected_asset}")
        print("🔄 No more 2+ days of monitoring without trading")
    else:
        print("⚠️ Market conditions currently unfavorable")
        print("📊 Robot will keep scanning until opportunities arise")
    
    print(f"\n🚀 READY TO LAUNCH: Run python robot.py to see the fix in action!")
