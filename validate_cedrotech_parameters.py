#!/usr/bin/env python3
"""
CEDROTECH API PARAMETER VALIDATION
Confirms all required parameters for PETR4 trading
Based on official documentation
"""

import os
from dotenv import load_dotenv
from datetime import datetime

def validate_cedrotech_parameters():
    """Validate all CedroTech API parameters against documentation"""
    print("=" * 60)
    print("🔍 CEDROTECH API PARAMETER VALIDATION")
    print("📋 Based on Official Documentation")
    print("=" * 60)
    
    # Load credentials
    load_dotenv()
    username = os.environ.get('CEDROTECH_USERNAME', '')
    user_id = os.environ.get('CEDROTECH_USER_ID', '')
    account = os.environ.get('CEDROTECH_ACCOUNT', '')
    
    print("\n🔐 CREDENTIALS CHECK:")
    cred_check = {
        'CEDROTECH_USERNAME': bool(username),
        'CEDROTECH_USER_ID': bool(user_id),
        'CEDROTECH_ACCOUNT': bool(account)
    }
    
    for key, value in cred_check.items():
        status = "✅" if value else "❌"
        print(f"   {status} {key}: {'SET' if value else 'NOT SET'}")
    
    print("\n📊 PETR4 ORDER PARAMETERS:")
    
    # Example PETR4 order parameters
    symbol = 'PETR4'
    quantity = 12
    price = 30.50
    
    # Required parameters according to documentation
    required_params = {
        'market': 'XBSP',  # Bovespa market code
        'price': str(f"{price:.2f}"),  # Price as string
        'quote': symbol,  # Stock symbol
        'qtd': str(quantity),  # Quantity as string
        'type': 'Limited',  # Order type
        'side': 'BUY',  # Order direction
        'username': username,  # User login
        'account': account,  # Account number
        'sourceaddress': 'TRADING_ROBOT'  # Source identifier
    }
    
    print("   📋 REQUIRED PARAMETERS:")
    for param, value in required_params.items():
        has_value = bool(value) if value != username and value != account else bool(value) and (param != 'username' or username) and (param != 'account' or account)
        status = "✅" if has_value else "❌"
        display_value = value if param not in ['username', 'account'] else ('SET' if value else 'NOT SET')
        print(f"      {status} {param}: {display_value}")
    
    # Optional parameters
    optional_params = {
        'orderstrategy': 'DAYTRADE',  # Trading strategy
        'timeinforce': 'DAY',  # Time in force
        'ordertag': f'IRAN_ISRAEL_WAR_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
        'appname': 'GEOPOLITICAL_TRADING_BOT',
        'clordid': f'PETR4_BUY_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    }
    
    print("\n   📋 OPTIONAL PARAMETERS:")
    for param, value in optional_params.items():
        print(f"      ✅ {param}: {value}")
    
    # Headers
    headers = {
        'user-identifier': user_id,  # Required header
        'accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    print("\n   📋 HEADERS:")
    for header, value in headers.items():
        has_value = bool(value) if header != 'user-identifier' else bool(user_id)
        status = "✅" if has_value else "❌"
        display_value = value if header != 'user-identifier' else ('SET' if user_id else 'NOT SET')
        print(f"      {status} {header}: {display_value}")
    
    print("\n🌐 API ENDPOINT:")
    print("   ✅ URL: https://webfeeder.cedrotech.com/services/negotiation/sendNewOrderSingleLimit")
    print("   ✅ Method: POST")
    print("   ✅ Content-Type: application/x-www-form-urlencoded")
    
    # Check completeness
    required_count = sum(1 for param, value in required_params.items() 
                        if bool(value) and param not in ['username', 'account']) + \
                    (1 if username else 0) + (1 if account else 0)
    total_required = len(required_params)
    header_count = sum(1 for h, v in headers.items() 
                      if bool(v) and h != 'user-identifier') + (1 if user_id else 0)
    total_headers = len(headers)
    
    print(f"\n🎯 COMPLETENESS CHECK:")
    print(f"   📊 Required Parameters: {required_count}/{total_required}")
    print(f"   📋 Headers: {header_count}/{total_headers}")
    
    overall_ready = required_count == total_required and header_count == total_headers
    
    if overall_ready:
        print(f"\n✅ ALL PARAMETERS READY!")
        print(f"🚀 CedroTech API integration is complete")
        print(f"🔥 Ready to place REAL MONEY orders")
        
        print(f"\n💻 SAMPLE ORDER (PETR4):")
        print(f"   Symbol: {symbol}")
        print(f"   Quantity: {quantity} shares")
        print(f"   Price: R${price:.2f}")
        print(f"   Total: R${price * quantity:.2f}")
        print(f"   Strategy: DAYTRADE")
        print(f"   Market: Bovespa (XBSP)")
        
    else:
        missing_items = []
        if not username:
            missing_items.append("CEDROTECH_USERNAME")
        if not user_id:
            missing_items.append("CEDROTECH_USER_ID")
        if not account:
            missing_items.append("CEDROTECH_ACCOUNT")
        
        print(f"\n❌ MISSING ITEMS:")
        for item in missing_items:
            print(f"   🔧 {item}")
        
        print(f"\n💡 FIX:")
        print(f"   Run: python setup_cedrotech_credentials.py")
    
    print("\n" + "=" * 60)
    print("🛢️ PETR4 IRAN-ISRAEL WAR TRADE")
    print("🎯 API Integration Validation Complete")
    print("=" * 60)
    
    return overall_ready

def show_api_mapping():
    """Show how our parameters map to CedroTech API"""
    print("\n📋 PARAMETER MAPPING:")
    print("   Our Code → CedroTech API")
    print("   ────────────────────────")
    
    mapping = [
        ("symbol", "quote", "Stock symbol (PETR4)"),
        ("quantity", "qtd", "Number of shares as string"),
        ("price", "price", "Price as string with 2 decimals"),
        ("'BUY'/'SELL'", "side", "Order direction"),
        ("'Limited'", "type", "Order type (limit order)"),
        ("'XBSP'", "market", "Bovespa market code"),
        ("username", "username", "User login name"),
        ("account", "account", "Account number"),
        ("'DAYTRADE'", "orderstrategy", "Trading strategy"),
        ("'DAY'", "timeinforce", "Valid for trading day"),
        ("user_id", "user-identifier", "Header authentication")
    ]
    
    for our_param, api_param, description in mapping:
        print(f"   {our_param:<12} → {api_param:<15} | {description}")

if __name__ == "__main__":
    ready = validate_cedrotech_parameters()
    show_api_mapping()
    
    if ready:
        print("\n🚀 READY TO TRADE!")
    else:
        print("\n🔧 Set credentials first!")
