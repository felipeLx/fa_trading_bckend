#!/usr/bin/env python3
"""
Daily Options Trading Startup Script
Run this every morning before starting options trading to verify system readiness.
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
from utils.balance_manager import BalanceManager
from options_robot import TRADEABLE_OPTIONS, MAX_RISK_PER_TRADE, load_options_state

load_dotenv()

def daily_options_startup_check():
    """Perform daily startup checks for the options trading robot."""
    print("🎯 DAILY OPTIONS TRADING STARTUP CHECK")
    print("=" * 60)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 1. Check Current Balance
        print("\n1️⃣ Checking Account Balance...")
        balance_manager = BalanceManager()
        balance_info = balance_manager.get_current_balance()
        
        if balance_info['success']:
            current_balance = balance_info['balance']
            print(f"   ✅ Current Balance: R${current_balance:.2f}")
            print(f"   📊 Source: {balance_info['source']}")
            print(f"   🎯 Max Risk Per Trade: R${current_balance * MAX_RISK_PER_TRADE:.2f} ({MAX_RISK_PER_TRADE*100}%)")
        else:
            print(f"   ❌ Balance check failed: {balance_info.get('error', 'Unknown error')}")
            current_balance = 0
        
        # 2. Check Options Robot State
        print("\n2️⃣ Checking Options Robot State...")
        options_state_file = 'options_robot_state.json'
        
        if os.path.exists(options_state_file):
            state = load_options_state()
            print(f"   ✅ Options state file found")
            print(f"   📅 Last trading date: {state.get('trading_date', 'Unknown')}")
            print(f"   📊 Daily trades count: {state.get('daily_trades_count', 0)}")
            print(f"   💰 Daily P&L: R${state.get('daily_pnl', 0):.2f}")
            
            # Check if holding any options
            holding_option = state.get('holding_option')
            if holding_option:
                print(f"   ⚠️ Currently holding: {holding_option}")
                print(f"   📦 Contracts: {state.get('option_contracts', 0)}")
                print(f"   💰 Entry price: R${state.get('entry_price', 0):.2f}")
            else:
                print(f"   ✅ No open positions")
        else:
            print("   ⚠️ Options state file not found - will be created on first run")
        
        # 3. Check Environment Variables
        print("\n3️⃣ Checking Configuration...")
        required_vars = ['USER_ID', 'SUPABASE_URL', 'SUPABASE_KEY']
        for var in required_vars:
            if os.getenv(var):
                print(f"   ✅ {var}: Set")
            else:
                print(f"   ❌ {var}: Missing")
        
        # 4. Check Market Hours
        print("\n4️⃣ Market Status Check...")
        now = datetime.now()
        hour = now.hour
        weekday = now.weekday()  # 0=Monday, 6=Sunday
        
        if weekday >= 5:  # Saturday or Sunday
            print("   🏖️ Weekend - Market Closed")
        elif hour < 9:
            print("   🌅 Pre-Market - Market opens at 09:00")
        elif hour >= 17:
            print("   🌆 After-Market - Market closed at 17:30")
        else:
            print("   📈 Market Hours - Options Trading Active")
        
        # 5. Check Target Options
        print("\n5️⃣ Target Options Configuration...")
        print(f"   🎯 Pre-qualified options: {len(TRADEABLE_OPTIONS)}")
        for i, option in enumerate(TRADEABLE_OPTIONS, 1):
            print(f"   {i}. {option['symbol']} (Score: {option['score']}, OI: {option['open_interest']:,})")
        
        # 6. Options Position Size Test
        print("\n6️⃣ Testing Options Position Sizing...")
        if current_balance > 0:
            # Test with example option price
            test_option_price = 0.50  # R$0.50 per contract
            max_risk = current_balance * MAX_RISK_PER_TRADE
            max_contracts = int(max_risk / test_option_price)
            max_contracts = min(max_contracts, 5)  # Conservative limit
            
            total_premium = max_contracts * test_option_price
            risk_percent = (total_premium / current_balance) * 100
            
            print(f"   ✅ Example: Option at R${test_option_price:.2f}")
            print(f"   📦 Max Contracts: {max_contracts}")
            print(f"   💰 Total Premium: R${total_premium:.2f}")
            print(f"   📊 Risk: {risk_percent:.2f}% of balance")
        else:
            print("   ❌ Cannot test position sizing without valid balance")
        
        print("\n" + "=" * 60)
        print("✅ OPTIONS STARTUP CHECK COMPLETE")
        
        # 7. Summary and Recommendations
        print("\n📋 STARTUP SUMMARY:")
        if weekday >= 5:
            print("   ⏰ Market closed (weekend) - wait for Monday")
        elif hour < 9:
            print("   ⏰ Market opens soon - prepare for testing")
        elif 9 <= hour <= 17:
            print("   🚀 READY FOR OPTIONS TRADING!")
            print("   📝 Next steps:")
            print("      1. python test_options_live_quotes.py  # Test live quotes")
            print("      2. python options_robot.py             # Start trading")
        else:
            print("   🌆 Market closed - prepare for tomorrow")
            
    except Exception as e:
        print(f"\n❌ Startup check failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    daily_options_startup_check()
