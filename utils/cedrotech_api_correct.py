#!/usr/bin/env python3
"""
Correct CedroTech API implementation using user-identifier header
Based on official API documentation requiring BASE64 encoded authentication
"""

import requests
import json
import base64
import time
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class CedroTechAPICorrect:
    """Correct CedroTech API implementation with proper user-identifier authentication"""
    
    def __init__(self, username=None, password=None, paper_trading=True):
        """
        Initialize CedroTech API with proper authentication.
        
        Args:
            username (str): Trading account username
            password (str): Trading account password  
            paper_trading (bool): If True, simulate orders without real execution
        """
        self.username = username or os.getenv('CEDROTECH_USERNAME', '')
        self.password = password or os.getenv('CEDROTECH_PASSWORD', '')
        self.paper_trading = paper_trading
        self.base_url = "https://webfeeder.cedrotech.com"
        self.user_identifier_header = None
        
        print(f"🔌 CedroTech API initialized (CORRECT IMPLEMENTATION)")
        print(f"   Mode: {'PAPER TRADING' if paper_trading else 'LIVE TRADING'}")
        print(f"   Username: {self.username}")
        
        # Generate user-identifier header on initialization
        self._generate_user_identifier()
    
    def _generate_user_identifier(self):
        """
        Generate the user-identifier header as per CedroTech documentation.
        Format: {"id":"1","user_name":"conta","login_oms":"conta","password":"senha","remote_ip":"ip"}
        Then BASE64 encode it.
        """
        try:
            # Create user identifier object as per documentation
            user_data = {
                "id": "1",
                "user_name": self.username,
                "login_oms": self.username,
                "password": self.password,
                "remote_ip": "127.0.0.1"  # Can be actual IP or localhost
            }
            
            # Convert to JSON string
            user_json = json.dumps(user_data, separators=(',', ':'))
            
            # BASE64 encode
            user_b64 = base64.b64encode(user_json.encode('utf-8')).decode('utf-8')
            
            self.user_identifier_header = user_b64
            
            print(f"✅ User-identifier generated successfully")
            print(f"   JSON: {user_json}")
            print(f"   BASE64: {user_b64[:50]}...")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to generate user-identifier: {e}")
            return False
    
    def test_authentication(self):
        """Test if the user-identifier works by making a simple API call"""
        if not self.user_identifier_header:
            print("❌ No user-identifier available")
            return False
        
        try:
            # Test with a simple order endpoint to verify authentication
            url = f"{self.base_url}/services/negotiation/sendNewOrderSingle"
            headers = {
                "accept": "application/json",
                "user-identifier": self.user_identifier_header
            }
            
            # Test parameters (minimal test)
            params = {
                "market": "XBSP",
                "quote": "PETR4",
                "qtd": "1", 
                "type": "Market",
                "side": "Buy",
                "username": self.username,
                "bypasssuitability": "true",
                "traderate": "0"
            }
            
            query_string = "&".join([f"{k}={v}" for k, v in params.items()])
            full_url = f"{url}?{query_string}"
            
            print(f"🧪 Testing authentication with API call...")
            print(f"   URL: {full_url}")
            print(f"   Headers: user-identifier provided")
            
            response = requests.post(full_url, headers=headers)
            
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            
            if response.status_code == 200:
                print("✅ Authentication successful!")
                return True
            elif response.status_code == 401:
                print("❌ Authentication failed - check credentials")
                return False
            else:
                print(f"⚠️  Unexpected response: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication test error: {e}")
            return False
    
    def place_buy_order(self, ticker, quantity, price=None, order_type="MARKET"):
        """
        Place a buy order with proper authentication.
        
        Args:
            ticker (str): Stock ticker (e.g., "PETR4")
            quantity (int): Number of shares to buy
            price (float): Limit price (for LIMIT orders)
            order_type (str): "MARKET", "LIMITED", "STOP", "START"
        
        Returns:
            dict: Order result with order_id and status
        """
        if self.paper_trading:
            return self._simulate_buy_order(ticker, quantity, price, order_type)
        
        if not self.user_identifier_header:
            return {"success": False, "error": "User-identifier not available"}
        
        try:
            # Map order types to CedroTech format
            cedro_order_type = {
                "MARKET": "Market",
                "LIMITED": "Limited", 
                "LIMIT": "Limited",
                "STOP": "Stop",
                "START": "Start"
            }.get(order_type.upper(), "Market")
            
            # Build parameters
            params = {
                "market": "XBSP",
                "quote": ticker,
                "qtd": str(quantity),
                "type": cedro_order_type,
                "side": "Buy",
                "username": self.username,
                "bypasssuitability": "true",
                "traderate": "0"
            }
            
            # Add price for limited orders
            if cedro_order_type == "Limited" and price:
                params["price"] = str(price)
            elif cedro_order_type == "Limited" and not price:
                return {"success": False, "error": "Price required for Limited orders"}
            
            # Build URL and headers
            url = f"{self.base_url}/services/negotiation/sendNewOrderSingle"
            query_string = "&".join([f"{k}={v}" for k, v in params.items()])
            full_url = f"{url}?{query_string}"
            
            headers = {
                "accept": "application/json",
                "user-identifier": self.user_identifier_header
            }
            
            print(f"🔄 Placing BUY order: {ticker} x{quantity}")
            print(f"   Type: {cedro_order_type}")
            if price:
                print(f"   Price: {price}")
            
            response = requests.post(full_url, headers=headers)
            
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            
            if response.status_code == 200:
                try:
                    result = response.json() if response.text else {}
                except:
                    result = {"raw_response": response.text}
                
                print(f"✅ BUY order submitted: {ticker} x{quantity}")
                return {
                    "success": True,
                    "order_id": result.get('orderId', f"ORDER_{int(time.time())}"),
                    "ticker": ticker,
                    "quantity": quantity,
                    "side": "BUY",
                    "status": "SUBMITTED",
                    "response": result
                }
            else:
                print(f"❌ BUY order failed: {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
                
        except Exception as e:
            print(f"❌ Buy order error: {e}")
            return {"success": False, "error": str(e)}
    
    def place_sell_order(self, ticker, quantity, price=None, order_type="MARKET"):
        """
        Place a sell order with proper authentication.
        
        Args:
            ticker (str): Stock ticker (e.g., "PETR4")
            quantity (int): Number of shares to sell
            price (float): Limit price (for LIMIT orders)
            order_type (str): "MARKET", "LIMITED", "STOP", "START"
        
        Returns:
            dict: Order result with order_id and status
        """
        if self.paper_trading:
            return self._simulate_sell_order(ticker, quantity, price, order_type)
        
        if not self.user_identifier_header:
            return {"success": False, "error": "User-identifier not available"}
        
        try:
            # Map order types to CedroTech format
            cedro_order_type = {
                "MARKET": "Market",
                "LIMITED": "Limited", 
                "LIMIT": "Limited",
                "STOP": "Stop",
                "START": "Start"
            }.get(order_type.upper(), "Market")
            
            # Build parameters
            params = {
                "market": "XBSP",
                "quote": ticker,
                "qtd": str(quantity),
                "type": cedro_order_type,
                "side": "Sell",
                "username": self.username,
                "bypasssuitability": "true",
                "traderate": "0"
            }
            
            # Add price for limited orders
            if cedro_order_type == "Limited" and price:
                params["price"] = str(price)
            elif cedro_order_type == "Limited" and not price:
                return {"success": False, "error": "Price required for Limited orders"}
            
            # Build URL and headers
            url = f"{self.base_url}/services/negotiation/sendNewOrderSingle"
            query_string = "&".join([f"{k}={v}" for k, v in params.items()])
            full_url = f"{url}?{query_string}"
            
            headers = {
                "accept": "application/json",
                "user-identifier": self.user_identifier_header
            }
            
            print(f"🔄 Placing SELL order: {ticker} x{quantity}")
            print(f"   Type: {cedro_order_type}")
            if price:
                print(f"   Price: {price}")
            
            response = requests.post(full_url, headers=headers)
            
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            
            if response.status_code == 200:
                try:
                    result = response.json() if response.text else {}
                except:
                    result = {"raw_response": response.text}
                
                print(f"✅ SELL order submitted: {ticker} x{quantity}")
                return {
                    "success": True,
                    "order_id": result.get('orderId', f"ORDER_{int(time.time())}"),
                    "ticker": ticker,
                    "quantity": quantity,
                    "side": "SELL",
                    "status": "SUBMITTED",
                    "response": result
                }
            else:
                print(f"❌ SELL order failed: {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
                
        except Exception as e:
            print(f"❌ Sell order error: {e}")
            return {"success": False, "error": str(e)}
    
    def _simulate_buy_order(self, ticker, quantity, price, order_type):
        """Simulate buy order for paper trading."""
        order_id = f"SIM_BUY_{int(time.time())}"
        print(f"📝 SIMULATED BUY: {ticker} x{quantity} ({order_type})")
        return {
            "success": True,
            "order_id": order_id,
            "ticker": ticker,
            "quantity": quantity,
            "side": "BUY",
            "status": "FILLED",
            "simulated": True
        }
    
    def _simulate_sell_order(self, ticker, quantity, price, order_type):
        """Simulate sell order for paper trading."""
        order_id = f"SIM_SELL_{int(time.time())}"
        print(f"📝 SIMULATED SELL: {ticker} x{quantity} ({order_type})")
        return {
            "success": True,
            "order_id": order_id,
            "ticker": ticker,
            "quantity": quantity,
            "side": "SELL",
            "status": "FILLED",
            "simulated": True
        }

def create_correct_cedrotech_api(paper_trading=True):
    """
    Factory function to create correct CedroTech API instance.
    
    Args:
        paper_trading (bool): True for simulation, False for live trading
    
    Returns:
        CedroTechAPICorrect: Configured API instance with proper authentication
    """
    return CedroTechAPICorrect(paper_trading=paper_trading)
