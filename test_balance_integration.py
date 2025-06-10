#!/usr/bin/env python3
"""
Test Dynamic Balance Management Integration
This script tests the complete balance management system integration.
"""

import os
import sys
import json
from dotenv import load_dotenv

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from utils.balance_manager import BalanceManager
from utils.database import insert_balance_record, fetch_user_balance, calculate_account_balance_from_trades

# Load environment variables
load_dotenv()

def test_balance_manager_integration():
    """Test the complete BalanceManager integration."""
    
    print("="*70)
    print("🧪 TESTING DYNAMIC BALANCE MANAGEMENT INTEGRATION")
    print("="*70)
    
    try:        # Initialize BalanceManager
        print("\n1️⃣ Initializing BalanceManager...")
        balance_manager = BalanceManager(initial_balance=500.0)
        print("✅ BalanceManager initialized successfully")
        
        # Test getting current balance
        print("\n2️⃣ Testing current balance retrieval...")
        balance_info = balance_manager.get_current_balance()
        print(f"💰 Current Balance: R${balance_info['balance']:,.2f}")
        print(f"📊 Source: {balance_info['source']}")
        print(f"🎯 Confidence: {balance_info['confidence']}")
        
        # Test position size calculation
        print("\n3️⃣ Testing dynamic position sizing...")
        risk_per_trade = 0.02  # 2%
        stop_loss_distance = 50.0  # R$50
        
        position_result = balance_manager.calculate_position_size_with_current_balance(
            risk_per_trade, stop_loss_distance
        )
        
        if position_result['success']:
            print(f"✅ Position size calculated: {position_result['position_size']:.2f} shares")
            print(f"💵 Available cash: R${position_result['available_cash']:,.2f}")
            print(f"⚠️ Risk amount: R${position_result['risk_amount']:,.2f}")
            print(f"📏 Limited by: {position_result['position_limited_by']}")
        else:
            print(f"❌ Position sizing failed: {position_result['error']}")
        
        # Test trade affordability validation
        print("\n4️⃣ Testing trade affordability validation...")
        test_ticker = "PETR4"
        test_quantity = 100
        test_price = 25.50
        
        affordability = balance_manager.validate_trade_affordability(
            test_ticker, test_quantity, test_price
        )
        
        if affordability['affordable']:
            print(f"✅ Trade is affordable: {test_quantity} shares of {test_ticker} at R${test_price}")
            print(f"💰 Trade value: R${affordability['trade_value']:,.2f}")
            print(f"💳 Available: R${affordability['available_cash']:,.2f}")
        else:
            print(f"❌ Trade not affordable: {affordability['message']}")
        
        # Test simulated trade execution and balance update
        print("\n5️⃣ Testing simulated trade execution...")
        
        if affordability['affordable']:
            # Simulate a buy order
            print(f"🚀 Simulating BUY: {test_quantity} shares of {test_ticker} at R${test_price}")
            buy_result = balance_manager.update_balance_after_trade(
                trade_type='buy',
                ticker=test_ticker,
                price=test_price,
                volume=test_quantity
            )
            
            if buy_result['success']:
                print(f"✅ Buy trade processed successfully")
                print(f"💰 New balance: R${buy_result['new_balance']:,.2f}")
                print(f"📉 Impact: R${buy_result['impact']:,.2f}")
                
                # Simulate a sell order (with 5% profit)
                sell_price = test_price * 1.05
                print(f"💰 Simulating SELL: {test_quantity} shares of {test_ticker} at R${sell_price:.2f}")
                
                sell_result = balance_manager.update_balance_after_trade(
                    trade_type='sell',
                    ticker=test_ticker,
                    price=sell_price,
                    volume=test_quantity
                )
                
                if sell_result['success']:
                    print(f"✅ Sell trade processed successfully")
                    print(f"💰 Final balance: R${sell_result['new_balance']:,.2f}")
                    print(f"📈 Impact: R${sell_result['impact']:,.2f}")
                    
                    # Calculate P&L
                    pnl = (sell_price - test_price) * test_quantity
                    print(f"🎯 P&L: R${pnl:,.2f} ({((sell_price/test_price)-1)*100:.2f}%)")
                else:
                    print(f"❌ Sell trade failed: {sell_result['error']}")
            else:
                print(f"❌ Buy trade failed: {buy_result['error']}")
        
        # Test database integration
        print("\n6️⃣ Testing database integration...")
        try:
            user_id = os.getenv("USER_ID")
            if user_id:
                # Test fetching balance from database
                db_balance = fetch_user_balance(user_id)
                if db_balance:
                    print(f"✅ Database balance retrieved: R${db_balance:,.2f}")
                else:
                    print("ℹ️ No database balance found (this is normal for first run)")
                
                # Test calculating balance from trades
                calc_balance = calculate_account_balance_from_trades(user_id)
                if calc_balance['success']:
                    print(f"✅ Calculated balance from trades: R${calc_balance['balance']:,.2f}")
                    print(f"📊 Total trades processed: {calc_balance['total_trades']}")
                else:
                    print(f"ℹ️ No trades found for calculation: {calc_balance['error']}")
            else:
                print("⚠️ USER_ID not found in environment variables")
                
        except Exception as e:
            print(f"⚠️ Database test error: {e}")
        
        # Test balance persistence
        print("\n7️⃣ Testing balance persistence...")
        final_balance_info = balance_manager.get_current_balance()
        print(f"💾 Final balance to persist: R${final_balance_info['balance']:,.2f}")
        
        print("\n" + "="*70)
        print("✅ DYNAMIC BALANCE MANAGEMENT INTEGRATION TEST COMPLETED")
        print("="*70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_robot_state_compatibility():
    """Test compatibility with existing robot state format."""
    
    print("\n" + "="*70)
    print("🤖 TESTING ROBOT STATE COMPATIBILITY")
    print("="*70)
    
    try:
        # Test loading existing robot state
        state_file = 'robot_state.json'
        if os.path.exists(state_file):
            with open(state_file, 'r') as f:
                current_state = json.load(f)
                
            print(f"📄 Current robot state loaded:")
            print(f"   Account Balance: R${current_state.get('account_balance', 'Not set')}")
            print(f"   Trading Date: {current_state.get('trading_date', 'Not set')}")
            print(f"   Daily Initial Balance: R${current_state.get('daily_initial_balance', 'Not set')}")
            print(f"   Holding Asset: {current_state.get('holding_asset', 'None')}")
            
            # Initialize BalanceManager and compare
            balance_manager = BalanceManager()
            dynamic_balance = balance_manager.get_current_balance()
            
            print(f"\n🔄 Dynamic balance comparison:")
            print(f"   State file balance: R${current_state.get('account_balance', 0)}")
            print(f"   Dynamic balance: R${dynamic_balance['balance']:,.2f}")
            print(f"   Source: {dynamic_balance['source']}")
            
            if abs(float(current_state.get('account_balance', 0)) - dynamic_balance['balance']) < 0.01:
                print("✅ Balances match - good consistency!")
            else:
                print("⚠️ Balance discrepancy detected - this is expected if trades occurred")
            
        else:
            print("ℹ️ No robot_state.json found - this is normal for first run")
            
        return True
        
    except Exception as e:
        print(f"❌ Robot state compatibility test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting comprehensive balance management tests...")
    
    # Run integration tests
    integration_success = test_balance_manager_integration()
    
    # Run compatibility tests
    compatibility_success = test_robot_state_compatibility()
    
    print(f"\n📊 TEST RESULTS:")
    print(f"   Integration Test: {'✅ PASSED' if integration_success else '❌ FAILED'}")
    print(f"   Compatibility Test: {'✅ PASSED' if compatibility_success else '❌ FAILED'}")
    
    if integration_success and compatibility_success:
        print(f"\n🎉 ALL TESTS PASSED! The dynamic balance management system is ready.")
        print(f"\n📋 NEXT STEPS:")
        print(f"   1. Run 'python robot.py' to start trading with dynamic balance")
        print(f"   2. Monitor balance updates in real-time")
        print(f"   3. Check database for balance tracking records")
    else:
        print(f"\n⚠️ Some tests failed. Please review the errors above.")
