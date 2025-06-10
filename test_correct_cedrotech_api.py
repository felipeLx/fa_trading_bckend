#!/usr/bin/env python3
"""
Test script for the correct CedroTech API implementation
Tests the user-identifier authentication method
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.cedrotech_api_correct import CedroTechAPICorrect
from dotenv import load_dotenv

load_dotenv()

def test_correct_cedrotech_api():
    """Test the correct CedroTech API implementation"""
    print("🧪 Testing CORRECT CedroTech API Implementation")
    print("=" * 60)
    
    # Initialize API with paper trading
    api = CedroTechAPICorrect(paper_trading=True)
    
    print("\n📋 Testing Authentication...")
    auth_result = api.test_authentication()
    
    if auth_result:
        print("✅ Authentication test passed!")
        
        print("\n📊 Testing Market Data...")
        # Test market data endpoint
        quote_data = api.get_quote("PETR4")
        print(f"Quote data: {quote_data}")
        
        print("\n💼 Testing Portfolio...")
        # Test portfolio data
        portfolio = api.get_portfolio()
        print(f"Portfolio: {portfolio}")
        
        print("\n📈 Testing Order Placement (PAPER MODE)...")
        # Test order placement in paper mode
        order_result = api.place_order(
            symbol="PETR4",
            side="Buy",
            quantity=100,
            order_type="Market"
        )
        print(f"Order result: {order_result}")
        
    else:
        print("❌ Authentication test failed!")
        print("🔍 Debugging authentication...")
        
        # Print debug info
        print(f"Username: {api.username}")
        print(f"Password: {'***' if api.password else 'Not set'}")
        print(f"User-identifier: {api.user_identifier_header[:50] if api.user_identifier_header else 'Not generated'}...")
    
    print("\n" + "=" * 60)
    print("✅ Test completed!")

if __name__ == "__main__":
    test_correct_cedrotech_api()
