#!/usr/bin/env python3
"""
Test the simplified CedroTech API approach
This tests the hypothesis that the API doesn't require SignIn authentication
"""

from utils.simple_cedrotech_api import create_simple_cedrotech_api

def test_simple_cedrotech_api():
    """Test the simplified CedroTech API"""
    print("="*60)
    print("TESTING SIMPLIFIED CEDROTECH API")
    print("="*60)
    print()

    # Test 1: Paper trading mode
    print("🧪 TEST 1: Paper Trading Mode")
    print("-" * 40)
    
    paper_api = create_simple_cedrotech_api(paper_trading=True)
    
    # Test buy order simulation
    buy_result = paper_api.place_buy_order('PETR4', 100, order_type='MARKET')
    print(f"Paper buy result: {buy_result['success']}")
    print()
    
    # Test 2: Live API test (small order)
    print("🧪 TEST 2: Live API Test")
    print("-" * 40)
    print("⚠️  CAUTION: This will attempt a real API call")
    print("   Testing with minimal order to check API response")
    print()
    
    live_api = create_simple_cedrotech_api(paper_trading=False)
    
    # Test with a very small order to see API response
    test_result = live_api.place_buy_order('PETR4', 1, price=30.50, order_type='LIMITED')
    
    print(f"Live API test result: {test_result}")
    print()
    
    if test_result.get('success'):
        print("✅ SIMPLIFIED API WORKING!")
        print("   ➤ No authentication required")
        print("   ➤ Direct order placement successful")
        print("   ➤ Ready for integration with robot.py")
    else:
        print("❌ API still requires additional setup")
        print("   ➤ Check error message above")
        print("   ➤ May need account activation or different credentials")
    
    print()
    print("="*60)
    print("NEXT STEPS:")
    if test_result.get('success'):
        print("1. Update robot.py to use SimpleCedroTechAPI")
        print("2. Remove complex authentication logic")
        print("3. Test with real day trading workflow")
    else:
        print("1. Contact CedroTech support about API access")
        print("2. Verify account has trading permissions")
        print("3. Check if additional API setup is required")
    print("="*60)

if __name__ == "__main__":
    test_simple_cedrotech_api()
