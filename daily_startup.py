#!/usr/bin/env python3
"""
Daily Trading Robot Startup Script
Run this every morning before starting trading to verify your system is ready.
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
from utils.balance_manager import BalanceManager

load_dotenv()

def daily_startup_check():
    """Perform daily startup checks for the trading robot."""
    
    print("🌅 DAILY TRADING ROBOT STARTUP CHECK")
    print("=" * 50)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # 1. Check Balance System
        print("1️⃣ Checking Balance System...")
        balance_manager = BalanceManager()
        balance_info = balance_manager.get_current_balance()
        
        print(f"   💰 Current Balance: R${balance_info['balance']:,.2f}")
        print(f"   📊 Source: {balance_info['source']}")
        print(f"   🎯 Confidence: {balance_info['confidence']}")
        print(f"   💵 Available Cash: R${balance_manager.get_available_cash():,.2f}")
        
        # 2. Check Robot State
        print("\n2️⃣ Checking Robot State...")
        state_file = 'robot_state.json'
        if os.path.exists(state_file):
            with open(state_file, 'r') as f:
                robot_state = json.load(f)
            
            print(f"   📄 State File Balance: R${robot_state.get('account_balance', 'Not set')}")
            print(f"   📅 Trading Date: {robot_state.get('trading_date', 'Not set')}")
            print(f"   📈 Holding Asset: {robot_state.get('holding_asset', 'None')}")
            
            # Update robot state with current date if needed
            today = datetime.now().strftime('%Y-%m-%d')
            if robot_state.get('trading_date') != today:
                robot_state['trading_date'] = today
                robot_state['daily_initial_balance'] = balance_info['balance']
                
                with open(state_file, 'w') as f:
                    json.dump(robot_state, f, indent=2)
                
                print(f"   ✅ Updated trading date to {today}")
        else:
            print("   ⚠️ Robot state file not found - will be created on first run")
        
        # 3. Check Environment Variables
        print("\n3️⃣ Checking Configuration...")
        required_vars = ['USER_ID', 'SUPABASE_URL', 'SUPABASE_KEY']
        for var in required_vars:
            if os.getenv(var):
                print(f"   ✅ {var}: Set")
            else:
                print(f"   ❌ {var}: Missing")
        
        # 4. Check Market Hours (Simple check for Brazilian market)
        now = datetime.now()
        hour = now.hour
        weekday = now.weekday()  # 0=Monday, 6=Sunday
        
        print("\n4️⃣ Market Status Check...")
        if weekday >= 5:  # Saturday or Sunday
            print("   🏖️ Weekend - Market Closed")
        elif hour < 10:
            print("   🌅 Pre-Market - Market opens at 10:00")
        elif hour >= 17:
            print("   🌆 After-Market - Market closed at 17:00")
        else:
            print("   📈 Market Hours - Trading Active")
        
        # 5. Position Size Test
        print("\n5️⃣ Testing Position Sizing...")
        position_result = balance_manager.calculate_position_size_with_current_balance(
            risk_per_trade=0.02,  # 2%
            stop_loss_distance=50.0
        )
        
        if position_result['success']:
            print(f"   ✅ Max Position Size: {position_result['position_size']:.2f} shares")
            print(f"   💰 Risk Amount: R${position_result['risk_amount']:,.2f}")
        else:
            print(f"   ❌ Position sizing error: {position_result['error']}")
        
        print("\n" + "=" * 50)
        print("✅ DAILY STARTUP CHECK COMPLETE")
        print("\n🚀 Ready to start trading! Run: python robot.py")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Startup check failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    daily_startup_check()
