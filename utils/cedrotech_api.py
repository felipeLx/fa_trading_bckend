"""
CedroTech API Integration for Day Trading Robot
Professional trading API connector with authentication and order management.
"""

import requests
import json
import time
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

class CedroTechAPI:
    """Professional CedroTech API connector for automated day trading."""
    def __init__(self, username=None, password=None, paper_trading=True):
        """
        Initialize CedroTech API connection.
        
        Args:
            username (str): Trading account username (default from env)
            password (str): Trading account password (default from env)
            paper_trading (bool): If True, simulate orders without real execution
        """        
        self.username = username or os.getenv('CEDROTECH_USERNAME', 'btg8778731')
        self.password = password or os.getenv('CEDROTECH_PASSWORD', '867790')
        self.paper_trading = paper_trading
        self.session_token = None
        self.user_identifier = None
        self.base_url = "https://webfeeder.cedrotech.com"
        self.authenticated = False
        
        print(f"🔌 CedroTech API initialized - Mode: {'PAPER TRADING' if paper_trading else 'LIVE TRADING'}")    
    
    def authenticate(self):
        """Authenticate with CedroTech API and obtain session token."""
        try:
            # URL encode password for special characters
            encoded_password = self.password.replace('@', '%40').replace('*', '%2A')
            url = f"{self.base_url}/SignIn?login={self.username}&password={encoded_password}"
            
            headers = {"accept": "application/json"}
            response = requests.post(url, headers=headers)
            
            print(f"🔍 Auth response status: {response.status_code}")
            print(f"🔍 Auth response text: {response.text[:200]}...")  # Debug info
            
            if response.status_code == 200:
                # Try to parse JSON response
                try:
                    response_data = response.json()
                    print(f"🔍 Response data type: {type(response_data)}")
                    print(f"🔍 Response data: {response_data}")
                    
                    # Handle different response formats
                    if isinstance(response_data, dict):
                        # Standard JSON response
                        self.user_identifier = response_data.get('userIdentifier') or response_data.get('user-identifier')
                        self.session_token = response_data.get('token') or response_data.get('sessionToken')
                    elif isinstance(response_data, bool) and response_data:
                        # Boolean response - authentication successful
                        self.user_identifier = self.username  # Use username as identifier
                        self.session_token = "authenticated"  # Simple token
                        print("🔍 Boolean response - using username as identifier")
                    else:
                        print(f"🔍 Unexpected response format: {response_data}")
                        return False
                        
                    self.authenticated = True
                    print("✅ CedroTech API authentication successful")
                    print(f"🔍 User identifier: {self.user_identifier}")
                    return True
                    
                except json.JSONDecodeError:
                    # Response is not JSON - check if it's a simple success response
                    if response.text.strip().lower() in ['true', 'success', 'ok']:
                        self.user_identifier = self.username
                        self.session_token = "authenticated"
                        self.authenticated = True
                        print("✅ CedroTech API authentication successful (non-JSON response)")
                        return True
                    else:
                        print(f"❌ Could not parse response: {response.text}")
                        return False
            else:
                print(f"❌ Authentication failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            print(f"🔍 Error type: {type(e)}")
            return False
    
    def check_authentication(self):
        """Check if authenticated, attempt to authenticate if not."""
        if not self.authenticated:
            return self.authenticate()
        return True
    
    def place_buy_order(self, ticker, quantity, price=None, order_type="MARKET"):
        """
        Place a buy order for day trading using CedroTech API.
        
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
        
        if not self.check_authentication():
            return {"success": False, "error": "Authentication failed"}
        
        if not self.user_identifier:
            return {"success": False, "error": "User identifier not available"}
        
        try:
            # Map order types to CedroTech format
            cedro_order_type = {
                "MARKET": "Market",
                "LIMITED": "Limited", 
                "LIMIT": "Limited",
                "STOP": "Stop",
                "START": "Start"
            }.get(order_type.upper(), "Market")
            
            # Build URL with required parameters
            url_params = {
                "market": "XBSP",  # Bovespa market
                "quote": ticker,
                "qtd": str(quantity),
                "type": cedro_order_type,
                "side": "Buy",
                "username": self.username,
                "bypasssuitability": "true",
                "traderate": "0",
                "orderstrategy": "DAYTRADE",  # Day trading strategy
                "timeinforce": "DAY"  # Day order
            }
            
            # Add price for limited orders
            if cedro_order_type == "Limited" and price:
                url_params["price"] = str(price)
            elif cedro_order_type == "Limited" and not price:
                return {"success": False, "error": "Price required for Limited orders"}
            
            # Build URL
            url = f"{self.base_url}/services/negotiation/sendNewOrderSingle"
            
            # Add query parameters to URL
            query_string = "&".join([f"{k}={v}" for k, v in url_params.items()])
            full_url = f"{url}?{query_string}"
            
            headers = {
                "accept": "application/json",
                "user-identifier": self.user_identifier
            }
            
            response = requests.post(full_url, headers=headers)
            
            if response.status_code in [200, 201]:
                result = response.json() if response.text else {}
                print(f"✅ BUY order placed: {ticker} x{quantity}")
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
                print(f"❌ BUY order failed: {response.status_code} - {response.text}")
                return {"success": False, "error": response.text}
                
        except Exception as e:
            print(f"❌ Buy order error: {e}")
            return {"success": False, "error": str(e)}
    
    def place_sell_order(self, ticker, quantity, price=None, order_type="MARKET"):
        """
        Place a sell order for day trading using CedroTech API.
        
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
        
        if not self.check_authentication():
            return {"success": False, "error": "Authentication failed"}
        
        if not self.user_identifier:
            return {"success": False, "error": "User identifier not available"}
        
        try:
            # Map order types to CedroTech format
            cedro_order_type = {
                "MARKET": "Market",
                "LIMITED": "Limited", 
                "LIMIT": "Limited",
                "STOP": "Stop",
                "START": "Start"
            }.get(order_type.upper(), "Market")
            
            # Build URL with required parameters
            url_params = {
                "market": "XBSP",  # Bovespa market
                "quote": ticker,
                "qtd": str(quantity),
                "type": cedro_order_type,
                "side": "Sell",  # Changed to Sell for sell orders
                "username": self.username,
                "bypasssuitability": "true",
                "traderate": "0",
                "orderstrategy": "DAYTRADE",  # Day trading strategy
                "timeinforce": "DAY"  # Day order
            }
            
            # Add price for limited orders
            if cedro_order_type == "Limited" and price:
                url_params["price"] = str(price)
            elif cedro_order_type == "Limited" and not price:
                return {"success": False, "error": "Price required for Limited orders"}
            
            # Build URL
            url = f"{self.base_url}/services/negotiation/sendNewOrderSingle"
            
            # Add query parameters to URL
            query_string = "&".join([f"{k}={v}" for k, v in url_params.items()])
            full_url = f"{url}?{query_string}"
            
            headers = {
                "accept": "application/json",
                "user-identifier": self.user_identifier
            }
            
            response = requests.post(full_url, headers=headers)
            
            if response.status_code in [200, 201]:
                result = response.json() if response.text else {}
                print(f"✅ SELL order placed: {ticker} x{quantity}")
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
                print(f"❌ SELL order failed: {response.status_code} - {response.text}")
                return {"success": False, "error": response.text}
                
        except Exception as e:
            print(f"❌ Sell order error: {e}")
            return {"success": False, "error": str(e)}
    
    def get_order_status(self, order_id):
        """Check the status of a specific order."""
        if self.paper_trading:
            return {"order_id": order_id, "status": "FILLED", "filled_quantity": 100}
        
        if not self.check_authentication():
            return {"error": "Authentication failed"}
        
        try:
            headers = {
                "accept": "application/json",
                "Authorization": f"Bearer {self.session_token}"
            }
            
            url = f"{self.base_url}/order/{order_id}"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Failed to get order status: {response.text}"}
                
        except Exception as e:
            return {"error": str(e)}
    
    def get_portfolio_positions(self):
        """Get current portfolio positions."""
        if self.paper_trading:
            return {"positions": [], "cash": 500.0}
        
        if not self.check_authentication():
            return {"error": "Authentication failed"}
        
        try:
            headers = {
                "accept": "application/json",
                "Authorization": f"Bearer {self.session_token}"
            }
            
            url = f"{self.base_url}/portfolio"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Failed to get portfolio: {response.text}"}
                
        except Exception as e:
            return {"error": str(e)}
    
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
    
    def close_all_positions(self):
        """Emergency function to close all open positions."""
        print("🚨 CLOSING ALL POSITIONS - DAY TRADING COMPLIANCE")
        
        positions = self.get_portfolio_positions()
        if "positions" in positions:
            for position in positions["positions"]:
                if position.get("quantity", 0) > 0:
                    ticker = position.get("symbol")
                    quantity = position.get("quantity")
                    result = self.place_sell_order(ticker, quantity, order_type="MARKET")
                    if result.get("success"):
                        print(f"✅ Closed position: {ticker} x{quantity}")
                    else:
                        print(f"❌ Failed to close: {ticker}")
        
        return True

# Factory function for easy integration
def create_cedrotech_api(paper_trading=True):
    """
    Factory function to create CedroTech API instance.
    
    Args:
        paper_trading (bool): True for simulation, False for live trading
    
    Returns:
        CedroTechAPI: Configured API instance
    """
    return CedroTechAPI(paper_trading=paper_trading)
