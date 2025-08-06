#!/usr/bin/env python3
"""
CedroTech Real Trading API Integration
For PETR4 Geopolitical Robot - REAL MONEY ORDERS
"""

import requests
import json
import os
from datetime import datetime
from typing import Dict, Optional

class CedroTechRealAPI:
    """
    Real CedroTech API for live trading
    WARNING: This places REAL MONEY orders!
    """
    
    def __init__(self):
        self.base_url = "https://webfeeder.cedrotech.com"
        self.market = "XBSP"  # Bovespa
        
        # API credentials (you need to set these)
        self.username = os.environ.get('CEDROTECH_USERNAME', '')
        self.user_identifier = os.environ.get('CEDROTECH_USER_ID', '')
        self.account = os.environ.get('CEDROTECH_ACCOUNT', '')
        
        if not all([self.username, self.user_identifier, self.account]):
            print("⚠️ WARNING: CedroTech credentials not set!")
            print("   Set environment variables:")
            print("   - CEDROTECH_USERNAME")
            print("   - CEDROTECH_USER_ID") 
            print("   - CEDROTECH_ACCOUNT")
    
    def place_buy_order(self, symbol: str, quantity: int, price: float) -> Dict:
        """
        Place a real BUY order through CedroTech API
        WARNING: This uses REAL MONEY!
        
        Based on CedroTech API Documentation:
        https://docs.cedrotech.com/reference/post_services-negotiation-sendnewordersinglelimit
        """
        print(f"🔥 PLACING REAL BUY ORDER:")
        print(f"   Symbol: {symbol}")
        print(f"   Quantity: {quantity}")
        print(f"   Price: R${price:.2f}")
        print(f"   Total: R${price * quantity:.2f}")
        
        # Prepare order parameters according to CedroTech API spec
        order_params = {
            # Required parameters
            'market': 'XBSP',  # Bovespa market code
            'price': str(f"{price:.2f}"),  # Price as string with 2 decimals
            'quote': symbol,  # Stock symbol (e.g., 'PETR4')
            'qtd': str(quantity),  # Quantity as string
            'type': 'Limited',  # Order type - exactly as documented
            'side': 'BUY',  # Order direction
            'username': self.username,  # User's login username
            'account': self.account,  # Account number
            'sourceaddress': 'TRADING_ROBOT',  # Source identifier
            
            # Optional but recommended parameters
            'orderstrategy': 'DAYTRADE',  # Day trade strategy
            'timeinforce': 'DAY',  # Valid for the trading day
            'ordertag': f'IRAN_ISRAEL_WAR_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'appname': 'GEOPOLITICAL_TRADING_BOT',
            'clordid': f'PETR4_BUY_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        }
        
        # Headers according to documentation
        headers = {
            'user-identifier': self.user_identifier,  # Required header
            'accept': 'application/json',  # Accept JSON response
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        try:
            # Make the API call
            url = f"{self.base_url}/services/negotiation/sendNewOrderSingleLimit"
            
            print(f"🌐 Sending order to CedroTech...")
            print(f"   URL: {url}")
            print(f"   Market: {order_params['market']}")
            print(f"   Strategy: {order_params['orderstrategy']}")
            
            response = requests.post(url, data=order_params, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"✅ ORDER SENT SUCCESSFULLY!")
                print(f"   Response: {result}")
                
                return {
                    'success': True,
                    'order_id': result.get('orderId', 'Unknown'),
                    'response': result,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                print(f"❌ ORDER FAILED!")
                print(f"   Status Code: {response.status_code}")
                print(f"   Response: {response.text}")
                
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}",
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            print(f"❌ API ERROR: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
      
    def place_sell_order(self, symbol: str, quantity: int, price: float) -> Dict:
        """
        Place a real SELL order through CedroTech API
        WARNING: This uses REAL MONEY!
        
        Based on CedroTech API Documentation:
        https://docs.cedrotech.com/reference/post_services-negotiation-sendnewordersinglelimit
        """
        print(f"🔥 PLACING REAL SELL ORDER:")
        print(f"   Symbol: {symbol}")
        print(f"   Quantity: {quantity}")
        print(f"   Price: R${price:.2f}")
        print(f"   Total: R${price * quantity:.2f}")
        
        # Prepare order parameters according to CedroTech API spec
        order_params = {
            # Required parameters
            'market': 'XBSP',  # Bovespa market code
            'price': str(f"{price:.2f}"),  # Price as string with 2 decimals
            'quote': symbol,  # Stock symbol (e.g., 'PETR4')
            'qtd': str(quantity),  # Quantity as string
            'type': 'Limited',  # Order type - exactly as documented
            'side': 'SELL',  # Order direction
            'username': self.username,  # User's login username
            'account': self.account,  # Account number
            'sourceaddress': 'TRADING_ROBOT',  # Source identifier
            
            # Optional but recommended parameters
            'orderstrategy': 'DAYTRADE',  # Day trade strategy
            'timeinforce': 'DAY',  # Valid for the trading day
            'ordertag': f'IRAN_ISRAEL_SELL_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'appname': 'GEOPOLITICAL_TRADING_BOT',
            'clordid': f'PETR4_SELL_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        }
        
        # Headers according to documentation
        headers = {
            'user-identifier': self.user_identifier,  # Required header
            'accept': 'application/json',  # Accept JSON response
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        try:
            # Make the API call
            url = f"{self.base_url}/services/negotiation/sendNewOrderSingleLimit"
            
            print(f"🌐 Sending SELL order to CedroTech...")
            print(f"   URL: {url}")
            print(f"   Market: {order_params['market']}")
            print(f"   Strategy: {order_params['orderstrategy']}")
            
            response = requests.post(url, data=order_params, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"✅ SELL ORDER SENT SUCCESSFULLY!")
                print(f"   Response: {result}")
                
                return {
                    'success': True,
                    'order_id': result.get('orderId', 'Unknown'),
                    'response': result,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                print(f"❌ SELL ORDER FAILED!")
                print(f"   Status Code: {response.status_code}")
                print(f"   Response: {response.text}")
                
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}",
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            print(f"❌ SELL order API error: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_current_quote(self, symbol: str) -> Optional[float]:
        """Get current market quote for symbol"""
        try:
            # This would use the quote API
            # For now, return estimated price
            return 30.50  # Fallback price
        except:
            return 30.50
