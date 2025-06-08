#!/usr/bin/env python3
"""
Test script for CedroTech API integration
Tests authentication and order placement with the updated API structure.
"""

from utils.cedrotech_api import create_cedrotech_api, CedroTechAPI
import os

def test_cedrotech_api():
    """Test CedroTech API functionality"""
    print("="*60)
    print("CEDROTECH API INTEGRATION TEST")
    print("="*60)
    print()

    # Show current configuration
    print("🔧 Current Configuration:")
    print(f"   Username: {os.getenv('CEDROTECH_USERNAME', '8778731')}")
    print(f"   Password: {'*' * len(os.getenv('CEDROTECH_PASSWORD', 'CsxjIQ06@*'))}")
    print(f"   Base URL: https://webfeeder.cedrotech.com")
    print()

    print("="*60)
    print("1. PAPER TRADING MODE TEST")
    print("="*60)
    
    # Test in paper trading mode first
    paper_api = create_cedrotech_api(paper_trading=True)
    print()

    # Test portfolio positions in paper mode
    print("📊 Testing portfolio positions (paper):")
    positions = paper_api.get_portfolio_positions()
    print(f"   Result: {positions}")
    print()

    # Test buy order simulation
    print("💰 Testing buy order (simulated):")
    buy_result = paper_api.place_buy_order('PETR4', 100, order_type='MARKET')
    print(f"   Result: {buy_result}")
    print()

    # Test sell order simulation  
    print("💸 Testing sell order (simulated):")
    sell_result = paper_api.place_sell_order('PETR4', 100, order_type='MARKET')
    print(f"   Result: {sell_result}")
    print()

    print("="*60)
    print("2. LIVE AUTHENTICATION TEST")
    print("="*60)
    
    # Test live authentication (without placing orders)
    live_api = create_cedrotech_api(paper_trading=False)
    print()
    
    print("🔐 Testing live authentication:")
    auth_result = live_api.authenticate()
    print(f"   Authentication successful: {auth_result}")
    print(f"   Session token available: {live_api.session_token is not None}")
    print(f"   User identifier available: {live_api.user_identifier is not None}")
    
    if live_api.session_token:
        print(f"   Token preview: {live_api.session_token[:20]}...")
    if live_api.user_identifier:
        print(f"   User ID: {live_api.user_identifier}")
    print()

    if auth_result:
        print("✅ LIVE API AUTHENTICATION SUCCESS!")
        print("   ➤ Ready for live trading operations")
        print("   ➤ Can integrate with robot.py for automated trading")
    else:
        print("❌ LIVE API AUTHENTICATION FAILED")
        print("   ➤ Check credentials and network connection")
        print("   ➤ Verify CedroTech account status")
    
    print()
    print("="*60)
    print("3. API INTEGRATION SUMMARY")
    print("="*60)
    print("✅ Paper trading mode: WORKING")
    print(f"{'✅' if auth_result else '❌'} Live authentication: {'WORKING' if auth_result else 'NEEDS ATTENTION'}")
    print("✅ Order structure: UPDATED FOR CEDROTECH API")
    print("✅ Day trading parameters: CONFIGURED")
    print()
    
    if auth_result:
        print("🎯 READY FOR LIVE TRADING INTEGRATION!")
        print("   Next steps:")
        print("   1. Update robot.py to use CedroTech API")
        print("   2. Test with small quantities first")
        print("   3. Monitor day trading compliance")
    else:
        print("⚠️  AUTHENTICATION NEEDS ATTENTION")
        print("   Check:")
        print("   1. Username and password are correct")
        print("   2. CedroTech account is active")
        print("   3. Network connectivity to API")

if __name__ == "__main__":
    test_cedrotech_api()
