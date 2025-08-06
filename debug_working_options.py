#!/usr/bin/env python3
"""
Debug version of Working Options Discovery
Quick test to see what data the API is actually returning
"""

import json
from datetime import datetime
from cedrotech_options_api import CedroTechOptionsAPI

def test_option_data_structure():
    """Test what data we're actually getting from the API"""
    print("🔍 DEBUG: Testing option data structure")
    print("=" * 50)
    
    # Initialize API
    api = CedroTechOptionsAPI()
    if not api.authenticate():
        print("❌ Failed to authenticate")
        return
    
    # Test with one VALE option that we know exists
    test_symbols = ['valeg560w4', 'valeg570w4', 'valeg580w4']
    
    for symbol in test_symbols:
        print(f"\n📊 Testing symbol: {symbol}")
        result = api.get_asset_info(symbol)
        
        if result.get('success'):
            data = result.get('data', {})
            print(f"   ✅ Success! Data type: {type(data)}")
            
            if isinstance(data, dict):
                print(f"   📋 Available keys: {list(data.keys())}")
                
                # Print all key-value pairs to see the structure
                print("   📄 Raw data:")
                for key, value in data.items():
                    if isinstance(value, (str, int, float, bool)) and value != "":
                        print(f"      {key}: {value}")
                
                # Look for price-related fields
                price_fields = ['bid', 'ask', 'last', 'lastTrade', 'price', 'lastPrice', 
                               'bidPrice', 'askPrice', 'currentBid', 'currentAsk']
                volume_fields = ['volume', 'dailyVolume', 'tradedVolume', 'vol']
                oi_fields = ['openInterest', 'interest', 'oi', 'openInt']
                
                print("   💰 Price data found:")
                for field in price_fields:
                    if field in data and data[field] not in [None, "", 0]:
                        print(f"      {field}: {data[field]}")
                
                print("   📊 Volume data found:")
                for field in volume_fields:
                    if field in data and data[field] not in [None, "", 0]:
                        print(f"      {field}: {data[field]}")
                
                print("   🎯 Open Interest data found:")
                for field in oi_fields:
                    if field in data and data[field] not in [None, "", 0]:
                        print(f"      {field}: {data[field]}")
                        
            else:
                print(f"   ⚠️ Data is not a dictionary: {data}")
        else:
            print(f"   ❌ Failed to get data for {symbol}")
            print(f"   Error: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    test_option_data_structure()
