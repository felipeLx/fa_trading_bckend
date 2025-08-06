#!/usr/bin/env python3
"""
PETR4 Geopolitical Trading Robot
Specialized robot for Iran-Israel conflict oil opportunity
Conservative approach with real money trading
"""

import json
import time
import os
import sys
import argparse  # Add argparse for command line arguments
from datetime import datetime, timedelta
from typing import Dict, Optional

# Add the current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from integrated_cedrotech_robot import IntegratedCedroTechRobot
from utils.database import fetch_intraday_prices
from cedrotech_real_api import CedroTechRealAPI

class PETR4GeopoliticalRobot:
    """
    Specialized robot for PETR4 geopolitical trading
    Features:
    - Conservative position sizing
    - Real money trading mode
    - Geopolitical event monitoring
    - Flexible exit strategies
    """
    
    def __init__(self, account_balance=500):
        self.robot_name = "PETR4 Geopolitical Robot"
        self.version = "1.0.0"
        self.account_balance = account_balance
        
        # Trading parameters - CONSERVATIVE
        self.target_symbol = 'PETR4'
        self.max_position_size = 12  # Conservative: 12 shares max
        self.stop_loss_percent = 4.0  # 4% stop loss
        self.take_profit_percent = 8.0  # 8% take profit
        self.max_investment = 360.0  # R$360 max (72% of capital)
        
        # Geopolitical parameters
        self.geopolitical_confidence_boost = 25  # Enhanced for war declaration
        self.min_confidence_for_entry = 75.0
        self.min_confidence_for_hold = 65.0
        
        # State management
        self.state_file = "petr4_geopolitical_robot_state.json"
        self.position = None
        self.entry_price = None
        self.entry_time = None
        self.paper_trading = False  # REAL MONEY MODE
          # Initialize base robot for analysis
        self.base_robot = IntegratedCedroTechRobot(paper_trading=True)
        
        # Initialize real trading API
        self.real_api = CedroTechRealAPI()
        
        # Load existing state
        self.load_state()
        
        print(f"🛢️ {self.robot_name} v{self.version} INITIALIZED")
        print(f"   🎯 Target: {self.target_symbol}")
        print(f"   💰 Max Investment: R${self.max_investment:.2f}")
        print(f"   📦 Max Position: {self.max_position_size} shares")
        print(f"   🌍 Geopolitical Mode: IRAN-ISRAEL CONFLICT")
        print(f"   💵 Mode: {'PAPER TRADING' if self.paper_trading else 'REAL MONEY'}")
    
    def load_state(self):
        """Load robot state from file"""
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                state = json.load(f)
                self.position = state.get('position')
                self.entry_price = state.get('entry_price')
                self.entry_time = state.get('entry_time')
                print(f"🔄 LOADED GEOPOLITICAL STATE:")
                print(f"   Position: {self.position}")
                print(f"   Entry Price: {self.entry_price}")
                print(f"   Entry Time: {self.entry_time}")
    
    def save_state(self):
        """Save robot state to file"""
        state = {
            'robot_name': self.robot_name,
            'version': self.version,
            'position': self.position,
            'entry_price': self.entry_price,
            'entry_time': self.entry_time,
            'last_update': datetime.now().isoformat()
        }
        
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def get_geopolitical_analysis(self):
        """Get enhanced analysis with geopolitical factors"""
        try:
            # Get base robot analysis
            base_analysis = self.base_robot.get_combined_analysis(self.target_symbol)
            
            # Current geopolitical factors
            geopolitical_factors = {
                'iran_israel_war': True,
                'oil_supply_threat': True,
                'brent_surge': True,
                'long_term_conflict': True
            }
            
            # Calculate geopolitical boost
            geo_boost = 0
            if geopolitical_factors['iran_israel_war']:
                geo_boost += 20  # War declaration
                print("   ⚡ Iran-Israel war declared: +20 points")
            
            if geopolitical_factors['oil_supply_threat']:
                geo_boost += 15  # Supply disruption
                print("   🛢️ Oil supply threat: +15 points")
            
            if geopolitical_factors['brent_surge']:
                geo_boost += 10  # Market confirmation
                print("   📈 Brent surge confirmed: +10 points")
            
            if geopolitical_factors['long_term_conflict']:
                geo_boost += 10  # Duration premium
                print("   ⏳ Long-term conflict expected: +10 points")
            
            # Enhanced confidence
            base_confidence = base_analysis['confidence']
            enhanced_confidence = min(95, base_confidence + geo_boost)
            
            return {
                'symbol': self.target_symbol,
                'base_signal': base_analysis['signal'],
                'base_confidence': base_confidence,
                'geopolitical_boost': geo_boost,
                'enhanced_confidence': enhanced_confidence,
                'recommendation': self.get_recommendation(enhanced_confidence),
                'analysis_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Analysis error: {e}")
            return None
    
    def get_recommendation(self, confidence):
        """Get trading recommendation based on confidence"""
        if confidence >= 85:
            return 'STRONG_BUY'
        elif confidence >= 75:
            return 'BUY'
        elif confidence >= 65:
            return 'HOLD'
        else:
            return 'SELL'
    
    def calculate_position_size(self, current_price):
        """Calculate conservative position size"""
        # Conservative approach: limit by both capital and risk
        max_shares_by_capital = int(self.max_investment / current_price)
        max_shares_absolute = self.max_position_size
        
        # Take the smaller (more conservative)
        position_size = min(max_shares_by_capital, max_shares_absolute)
        
        total_investment = position_size * current_price
        capital_usage = (total_investment / self.account_balance) * 100
        
        print(f"   📊 Position Sizing:")
        print(f"      💰 Current Price: R${current_price:.2f}")
        print(f"      📦 Position Size: {position_size} shares")
        print(f"      💵 Total Investment: R${total_investment:.2f}")
        print(f"      📊 Capital Usage: {capital_usage:.1f}%")
        
        return position_size, total_investment
    
    def should_enter_position(self):
        """Check if we should enter a position"""
        if self.position is not None:
            return False, "Already in position"
        
        analysis = self.get_geopolitical_analysis()
        if not analysis:
            return False, "Analysis failed"
        
        if analysis['enhanced_confidence'] < self.min_confidence_for_entry:
            return False, f"Confidence too low: {analysis['enhanced_confidence']:.1f}%"
        
        if analysis['recommendation'] not in ['BUY', 'STRONG_BUY']:
            return False, f"No buy signal: {analysis['recommendation']}"
        
        return True, analysis
    
    def should_exit_position(self, current_price):
        """Check if we should exit current position"""
        if not self.position or not self.entry_price:
            return False, "No position to exit"
        
        # Calculate P&L
        pnl_percent = ((current_price - self.entry_price) / self.entry_price) * 100
        
        # Stop loss check
        if pnl_percent <= -self.stop_loss_percent:
            return True, f"STOP LOSS triggered: {pnl_percent:.2f}%"
        
        # Take profit check
        if pnl_percent >= self.take_profit_percent:
            return True, f"TAKE PROFIT triggered: {pnl_percent:.2f}%"
        
        # Geopolitical exit check
        analysis = self.get_geopolitical_analysis()
        if analysis and analysis['enhanced_confidence'] < self.min_confidence_for_hold:
            return True, f"Confidence dropped: {analysis['enhanced_confidence']:.1f}%"
        
        # Time-based exit (end of day)
        now = datetime.now()
        if now.hour >= 17:  # After 5 PM
            return True, "End of day exit"
        
        return False, f"HOLD - P&L: {pnl_percent:.2f}%"
    def execute_buy_order(self, price, shares):
        """Execute buy order using real CedroTech API"""
        print(f"\n🔥 EXECUTING BUY ORDER:")
        print(f"   📊 Symbol: {self.target_symbol}")
        print(f"   💰 Price: R${price:.2f}")
        print(f"   📦 Shares: {shares}")
        print(f"   💵 Total: R${price * shares:.2f}")
        
        if self.paper_trading:
            # Simulated execution
            print("   🎮 SIMULATED ORDER EXECUTED")
            success = True
        else:
            # Real execution using CedroTech API
            print("   💰 PLACING REAL ORDER VIA CEDROTECH API")
            order_result = self.real_api.place_buy_order(
                symbol=self.target_symbol,
                quantity=shares,
                price=price
            )
            success = order_result.get('success', False)
        
        if success:
            self.position = shares
            self.entry_price = price
            self.entry_time = datetime.now().isoformat()
            self.save_state()
            
            print(f"   ✅ BUY ORDER SUCCESSFUL")
            print(f"   📦 Position: {self.position} shares")
            print(f"   💰 Entry: R${self.entry_price:.2f}")
            
            return True
        else:
            print(f"   ❌ BUY ORDER FAILED")
            return False
    def execute_sell_order(self, price, reason):
        """Execute sell order through CedroTech API"""
        if not self.position:
            print(f"❌ No position to sell!")
            return False
        
        print(f"\n🔥 EXECUTING SELL ORDER:")
        print(f"   Symbol: {self.target_symbol}")
        print(f"   Shares: {self.position}")
        print(f"   Price: R${price:.2f}")
        print(f"   Reason: {reason}")
        
        # Calculate P&L
        if self.entry_price:
            pnl = (price - self.entry_price) * self.position
            pnl_percent = ((price - self.entry_price) / self.entry_price) * 100
            print(f"   💰 P&L: R${pnl:.2f} ({pnl_percent:.2f}%)")
        
        try:
            # Execute real sell order
            order_result = self.real_api.place_sell_order(
                symbol=self.target_symbol,
                quantity=self.position,
                price=price
            )
            
            if order_result.get('success'):
                print(f"✅ SELL ORDER PLACED SUCCESSFULLY!")
                print(f"   Order ID: {order_result.get('order_id')}")
                
                # Clear position
                self.position = None
                self.entry_price = None
                self.save_state()
                
                # Log the trade
                self.log_trade('SELL', self.target_symbol, self.position, price, reason)
                
                return True
            else:
                print(f"❌ SELL ORDER FAILED!")
                print(f"   Error: {order_result.get('error')}")
                return False
                
        except Exception as e:
            print(f"❌ Sell order error: {e}")
            return False
    
    def handle_manual_sell(self):
        """Handle manual sell command"""
        if not self.position:
            print(f"❌ No active PETR4 position to sell!")
            return False
        
        print(f"📊 Current Position:")
        print(f"   Symbol: {self.target_symbol}")
        print(f"   Shares: {self.position}")
        print(f"   Entry Price: R${self.entry_price:.2f}")
        
        current_price = self.get_current_price()
        print(f"   Current Price: R${current_price:.2f}")
        
        if self.entry_price:
            pnl = (current_price - self.entry_price) * self.position
            pnl_percent = ((current_price - self.entry_price) / self.entry_price) * 100
            print(f"   Current P&L: R${pnl:.2f} ({pnl_percent:.2f}%)")
        
        confirm = input(f"\n🔥 Confirm SELL {self.position} shares of {self.target_symbol}? (y/n): ")
        
        if confirm.lower().strip() == 'y':
            return self.execute_sell_order(current_price, "Manual sell command")
        else:
            print(f"👋 Sell cancelled")
            return False
    
    def get_current_price(self):
        """Get current PETR4 price"""
        try:
            # Try to get real price from data source
            prices = fetch_intraday_prices(self.target_symbol)
            if prices and len(prices) > 0:
                return prices[0]['close']
            else:
                # Fallback to estimated price
                return 30.50  # Estimated based on futures
        except Exception as e:
            print(f"⚠️ Price fetch error: {e}")
            return 30.50  # Fallback price
    
    def run_trading_cycle(self):
        """Run one complete trading cycle"""
        print(f"\n{'='*60}")
        print(f"🛢️ PETR4 GEOPOLITICAL TRADING CYCLE")
        print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   🌍 Context: Iran-Israel War Declared")
        print(f"{'='*60}")
        
        try:
            current_price = self.get_current_price()
            print(f"📊 Current {self.target_symbol} Price: R${current_price:.2f}")
            
            if not self.position:
                # Check for entry opportunity
                should_enter, result = self.should_enter_position()
                
                if should_enter:
                    analysis = result
                    position_size, investment = self.calculate_position_size(current_price)
                    
                    print(f"\n🚀 ENTRY SIGNAL DETECTED:")
                    print(f"   🎯 Enhanced Confidence: {analysis['enhanced_confidence']:.1f}%")
                    print(f"   💪 Recommendation: {analysis['recommendation']}")
                    print(f"   🌍 Geopolitical Boost: +{analysis['geopolitical_boost']} points")
                    
                    if self.execute_buy_order(current_price, position_size):
                        print(f"   ✅ POSITION OPENED SUCCESSFULLY")
                    else:
                        print(f"   ❌ FAILED TO OPEN POSITION")
                else:
                    print(f"❌ NO ENTRY SIGNAL: {result}")
            
            else:
                # Monitor existing position
                should_exit, reason = self.should_exit_position(current_price)
                
                pnl = (current_price - self.entry_price) * self.position
                pnl_percent = ((current_price - self.entry_price) / self.entry_price) * 100
                
                print(f"\n👀 MONITORING POSITION:")
                print(f"   📦 Position: {self.position} shares")
                print(f"   💰 Entry: R${self.entry_price:.2f}")
                print(f"   📊 Current: R${current_price:.2f}")
                print(f"   📈 P&L: R${pnl:.2f} ({pnl_percent:.2f}%)")
                
                if should_exit:
                    print(f"\n🚨 EXIT SIGNAL: {reason}")
                    if self.execute_sell_order(current_price, reason):
                        print(f"   ✅ POSITION CLOSED SUCCESSFULLY")
                        return "POSITION_CLOSED"
                    else:
                        print(f"   ❌ FAILED TO CLOSE POSITION")
                else:
                    print(f"✅ HOLDING POSITION: {reason}")
            
            return "CYCLE_COMPLETE"
            
        except Exception as e:
            print(f"❌ TRADING CYCLE ERROR: {e}")
            import traceback
            traceback.print_exc()
            return "ERROR"
    
    def run_market_open_strategy(self):
        """Special strategy for market open"""
        print(f"\n🔥 MARKET OPEN GEOPOLITICAL STRATEGY")
        print(f"🌍 Iran-Israel War Declared - Oil Opportunity")
        print(f"⏰ Waiting for market open...")
        
        # Wait for market open if needed
        now = datetime.now()
        if now.hour < 9:
            wait_minutes = (9 - now.hour) * 60 - now.minute
            print(f"   ⏳ Market opens in {wait_minutes} minutes")
            print(f"   🎯 Will start trading at 09:00")
        
        # Run initial analysis
        analysis = self.get_geopolitical_analysis()
        if analysis:
            print(f"\n📊 PRE-MARKET ANALYSIS:")
            print(f"   🎯 Enhanced Confidence: {analysis['enhanced_confidence']:.1f}%")
            print(f"   💪 Recommendation: {analysis['recommendation']}")
            print(f"   🌍 Geopolitical Boost: +{analysis['geopolitical_boost']} points")
            
            if analysis['enhanced_confidence'] >= self.min_confidence_for_entry:
                print(f"   ✅ READY FOR MARKET OPEN TRADE")
            else:
                print(f"   ⚠️ Confidence below entry threshold")
        
        return analysis

def main():
    """Main function for PETR4 geopolitical trading"""
    print("🛢️ PETR4 GEOPOLITICAL TRADING ROBOT")
    print("🌍 Iran-Israel War Oil Opportunity")
    print("=" * 60)
    
    parser = argparse.ArgumentParser(description='PETR4 Geopolitical Trading Robot')
    parser.add_argument('--sell', type=float, nargs=2, metavar=('PRICE', 'SHARES'),
                        help='Execute a manual sell order at given PRICE for SHARES number of shares')
    args = parser.parse_args()
    
    # Initialize robot
    robot = PETR4GeopoliticalRobot(account_balance=500)
    
    if args.sell:
        # Manual sell order
        price, shares = args.sell
        print(f"\n💼 MANUAL SELL ORDER REQUESTED:")
        print(f"   📊 Symbol: {robot.target_symbol}")
        print(f"   💰 Price: R${price:.2f}")
        print(f"   📦 Shares: {shares}")
        
        robot.execute_sell_order(price, "Manual sell order")
    else:
        # Run market open strategy
        pre_analysis = robot.run_market_open_strategy()
        
        if pre_analysis and pre_analysis['enhanced_confidence'] >= 75:
            print(f"\n🚀 HIGH CONFIDENCE DETECTED!")
            print(f"   Ready for aggressive market open entry")
            
            response = input("\nExecute market open trade? (y/n): ").lower().strip()
            
            if response == 'y':
                print(f"\n🔥 STARTING GEOPOLITICAL TRADING...")
                
                # Run initial cycle
                result = robot.run_trading_cycle()
                
                if result == "CYCLE_COMPLETE":
                    print(f"\n🎯 Continue monitoring? (y/n): ", end="")
                    monitor = input().lower().strip()
                    
                    if monitor == 'y':
                        print(f"\n🔄 STARTING CONTINUOUS MONITORING...")
                        print(f"   Will check every 15 minutes")
                        print(f"   Press Ctrl+C to stop")
                        
                        try:
                            while True:
                                time.sleep(15 * 60)  # 15 minutes
                                result = robot.run_trading_cycle()
                                
                                if result == "POSITION_CLOSED":
                                    print(f"\n🎉 TRADE COMPLETED!")
                                    break
                                    
                        except KeyboardInterrupt:
                            print(f"\n🛑 MONITORING STOPPED BY USER")
                            
                            if robot.position:
                                close_pos = input("Close position before exit? (y/n): ").lower()
                                if close_pos == 'y':
                                    current_price = robot.get_current_price()
                                    robot.execute_sell_order(current_price, "Manual exit")
            else:
                print(f"👋 Trade cancelled - staying in analysis mode")
        else:
            print(f"\n⚠️ Confidence below entry threshold")
            print(f"   Monitor for better entry point")

if __name__ == "__main__":
    main()
