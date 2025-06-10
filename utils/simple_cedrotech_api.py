"""
Simplified CedroTech API - No Authentication Required
Based on analysis that the API might be stateless and username-based
"""

import requests
import json
import time
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class SimpleCedroTechAPI:
    """Simplified CedroTech API that doesn't require SignIn authentication"""
    
    def __init__(self, username=None, paper_trading=True):
        """
        Initialize simplified CedroTech API.
        
        Args:
            username (str): Trading account username
            paper_trading (bool): If True, simulate orders without real execution
        """
        self.username = username or os.getenv('CEDROTECH_USERNAME', '')
        self.paper_trading = paper_trading
        self.base_url = "https://webfeeder.cedrotech.com"
        
        print(f"🔌 Simple CedroTech API initialized")
        print(f"   Mode: {'PAPER TRADING' if paper_trading else 'LIVE TRADING'}")
        print(f"   Username: {self.username}")
    
    def place_buy_order(self, ticker, quantity, price=None, order_type="MARKET"):
        """
        Place a buy order using the direct API approach.
        
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
        
        try:
            # Map order types to CedroTech format
            cedro_order_type = {
                "MARKET": "Market",
                "LIMITED": "Limited", 
                "LIMIT": "Limited",
                "STOP": "Stop",
                "START": "Start"
            }.get(order_type.upper(), "Market")
            
            # Build parameters exactly like your working example
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
            
            # Build URL with query parameters
            url = f"{self.base_url}/services/negotiation/sendNewOrderSingle"
            query_string = "&".join([f"{k}={v}" for k, v in params.items()])
            full_url = f"{url}?{query_string}"
            
            headers = {"accept": "application/json"}
            
            print(f"🔄 Placing BUY order: {ticker} x{quantity}")
            print(f"   URL: {full_url}")
            
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
        Place a sell order using the direct API approach.
        
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
            
            # Build URL
            url = f"{self.base_url}/services/negotiation/sendNewOrderSingle"
            query_string = "&".join([f"{k}={v}" for k, v in params.items()])
            full_url = f"{url}?{query_string}"
            
            headers = {"accept": "application/json"}
            
            print(f"🔄 Placing SELL order: {ticker} x{quantity}")
            print(f"   URL: {full_url}")
            
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

def create_simple_cedrotech_api(paper_trading=True):
    """
    Factory function to create simplified CedroTech API instance.
    
    Args:
        paper_trading (bool): True for simulation, False for live trading
    
    Returns:
        SimpleCedroTechAPI: Configured API instance
    """
    return SimpleCedroTechAPI(paper_trading=paper_trading)
