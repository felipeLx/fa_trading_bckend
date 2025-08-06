#!/usr/bin/env python3
"""
REAL-TIME MARKET MONITOR
Live tracking for PETR4 Iran-Israel War Trade
Monitors price, P&L, geopolitical events, and exit signals
"""

import time
import json
import os
import requests
from datetime import datetime, timedelta
from typing import Dict, Optional

class RealTimeMarketMonitor:
    """
    Real-time monitoring for active PETR4 position
    Tracks price movements, P&L, and exit signals
    """
    
    def __init__(self):
        self.symbol = 'PETR4'
        self.monitor_name = "PETR4 War Trade Monitor"
        self.position_file = "petr4_geopolitical_robot_state.json"
        
        # Trading parameters
        self.stop_loss_percent = 4.0
        self.take_profit_percent = 8.0
        self.monitoring_interval = 900  # 15 minutes = 900 seconds
        
        # Market hours (B3)
        self.market_open = "10:00"
        self.market_close = "17:30"
        
        # Load position if exists
        self.position = self.load_position()
        
    def load_position(self):
        """Load current position from state file"""
        try:
            if os.path.exists(self.position_file):
                with open(self.position_file, 'r') as f:
                    state = json.load(f)
                    return state.get('position')
            return None
        except Exception as e:
            print(f"❌ Error loading position: {e}")
            return None
    
    def get_current_price(self):
        """Get current PETR4 price"""
        try:
            # In real implementation, this would connect to your price feed
            # For now, simulate with last known price
            print(f"📊 Fetching {self.symbol} current price...")
            
            # You would replace this with actual price API call
            # Example: Yahoo Finance, Alpha Vantage, or your broker's API
            
            # Simulated price (replace with real API)
            import random
            base_price = 30.00  # Approximate PETR4 price
            volatility = 0.02   # 2% volatility
            current_price = base_price * (1 + random.uniform(-volatility, volatility))
            
            print(f"💰 {self.symbol}: R${current_price:.2f}")
            return current_price
            
        except Exception as e:
            print(f"❌ Price fetch error: {e}")
            return None
    
    def calculate_pnl(self, current_price):
        """Calculate current P&L"""
        if not self.position or not current_price:
            return None
        
        entry_price = self.position.get('entry_price', 0)
        shares = self.position.get('shares', 0)
        
        if entry_price <= 0 or shares <= 0:
            return None
        
        # Calculate P&L
        total_cost = entry_price * shares
        current_value = current_price * shares
        pnl_amount = current_value - total_cost
        pnl_percent = (pnl_amount / total_cost) * 100
        
        return {
            'entry_price': entry_price,
            'current_price': current_price,
            'shares': shares,
            'total_cost': total_cost,
            'current_value': current_value,
            'pnl_amount': pnl_amount,
            'pnl_percent': pnl_percent
        }
    
    def check_exit_signals(self, pnl_data):
        """Check if we should exit the position"""
        if not pnl_data:
            return False, "No P&L data"
        
        pnl_percent = pnl_data['pnl_percent']
        
        # Stop loss check
        if pnl_percent <= -self.stop_loss_percent:
            return True, f"STOP LOSS triggered: {pnl_percent:.2f}%"
        
        # Take profit check
        if pnl_percent >= self.take_profit_percent:
            return True, f"TAKE PROFIT triggered: {pnl_percent:.2f}%"
        
        # Time-based exit (near market close)
        now = datetime.now()
        market_close_time = now.replace(hour=17, minute=15, second=0, microsecond=0)
        
        if now >= market_close_time:
            return True, f"MARKET CLOSE approaching: {pnl_percent:.2f}%"
        
        return False, "Continue holding"
    
    def display_position_status(self, pnl_data):
        """Display current position status"""
        print("\n" + "=" * 50)
        print(f"📊 {self.monitor_name}")
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        
        if not pnl_data:
            print("❌ No position or price data available")
            return
        
        # Position details
        print(f"🎯 Symbol: {self.symbol}")
        print(f"📦 Shares: {pnl_data['shares']}")
        print(f"💵 Entry Price: R${pnl_data['entry_price']:.2f}")
        print(f"💰 Current Price: R${pnl_data['current_price']:.2f}")
        print(f"💸 Total Cost: R${pnl_data['total_cost']:.2f}")
        print(f"💎 Current Value: R${pnl_data['current_value']:.2f}")
        
        # P&L with color coding
        pnl_amount = pnl_data['pnl_amount']
        pnl_percent = pnl_data['pnl_percent']
        
        if pnl_amount >= 0:
            print(f"📈 P&L: +R${pnl_amount:.2f} (+{pnl_percent:.2f}%) 🟢")
        else:
            print(f"📉 P&L: R${pnl_amount:.2f} ({pnl_percent:.2f}%) 🔴")
        
        # Risk levels
        stop_loss_price = pnl_data['entry_price'] * (1 - self.stop_loss_percent / 100)
        take_profit_price = pnl_data['entry_price'] * (1 + self.take_profit_percent / 100)
        
        print(f"\n⚠️ RISK LEVELS:")
        print(f"🛑 Stop Loss: R${stop_loss_price:.2f} ({-self.stop_loss_percent}%)")
        print(f"🎯 Take Profit: R${take_profit_price:.2f} (+{self.take_profit_percent}%)")
        
        # Distance to levels
        distance_to_stop = ((pnl_data['current_price'] - stop_loss_price) / stop_loss_price) * 100
        distance_to_profit = ((take_profit_price - pnl_data['current_price']) / pnl_data['current_price']) * 100
        
        print(f"📏 Distance to Stop: {distance_to_stop:.1f}%")
        print(f"📏 Distance to Profit: {distance_to_profit:.1f}%")
    
    def display_geopolitical_update(self):
        """Display current geopolitical situation"""
        print(f"\n⚡ GEOPOLITICAL UPDATE:")
        print(f"🇮🇷🇮🇱 Iran-Israel War: ONGOING")
        print(f"🛢️ Oil Impact: BULLISH for PETR4")
        print(f"📰 News Flow: Monitor for escalation")
        print(f"⏰ Market Sentiment: WAR PREMIUM")
    
    def monitor_cycle(self):
        """Run one monitoring cycle"""
        print(f"\n🔄 Starting monitoring cycle...")
        
        # Get current price
        current_price = self.get_current_price()
        if not current_price:
            print("❌ Cannot get price, skipping cycle")
            return
        
        # Calculate P&L
        pnl_data = self.calculate_pnl(current_price)
        
        # Display status
        self.display_position_status(pnl_data)
        self.display_geopolitical_update()
        
        # Check exit signals
        should_exit, exit_reason = self.check_exit_signals(pnl_data)
        
        if should_exit:
            print(f"\n🚨 EXIT SIGNAL: {exit_reason}")
            print(f"🔥 RECOMMENDATION: SELL {self.symbol} NOW!")
            print(f"💻 COMMAND: python petr4_geopolitical_robot.py --sell")
            return True  # Signal to stop monitoring
        
        print(f"\n✅ Position Status: HOLD")
        print(f"⏰ Next check in 15 minutes...")
        return False  # Continue monitoring
    
    def start_monitoring(self):
        """Start real-time monitoring"""
        print("🚀 Starting Real-Time Market Monitor")
        print(f"📊 Symbol: {self.symbol}")
        print(f"⏰ Interval: {self.monitoring_interval / 60} minutes")
        print(f"🛑 Stop Loss: {self.stop_loss_percent}%")
        print(f"🎯 Take Profit: {self.take_profit_percent}%")
        
        if not self.position:
            print("❌ No active position found!")
            print("💡 Run this after executing the PETR4 buy order")
            return
        
        print(f"✅ Active position found: {self.position}")
        
        try:
            cycle_count = 0
            while True:
                cycle_count += 1
                print(f"\n{'='*60}")
                print(f"🔄 MONITORING CYCLE #{cycle_count}")
                print(f"{'='*60}")
                
                # Run monitoring cycle
                should_stop = self.monitor_cycle()
                
                if should_stop:
                    print(f"\n🏁 Monitoring stopped: Exit signal triggered")
                    break
                
                # Wait for next cycle
                print(f"\n⏰ Waiting {self.monitoring_interval / 60} minutes...")
                time.sleep(self.monitoring_interval)
                
        except KeyboardInterrupt:
            print(f"\n🛑 Monitoring stopped by user")
        except Exception as e:
            print(f"\n❌ Monitoring error: {e}")

def main():
    """Main monitoring function"""
    monitor = RealTimeMarketMonitor()
    
    # Check if we have an active position
    if not monitor.position:
        print("📋 No active PETR4 position found.")
        print("💡 This monitor should be run AFTER placing the buy order.")
        print("🔥 Commands:")
        print("   1. python petr4_geopolitical_robot.py    # Place buy order")
        print("   2. python real_time_market_monitor.py     # Start monitoring")
        return
    
    # Start monitoring
    monitor.start_monitoring()

if __name__ == "__main__":
    main()
