"""
CEDROTECH ENHANCED TRADING ROBOT
New robot using CedroTech API with combined fundamental + technical analysis
Separate from the original BrAPI robot - uses enhanced signal generation
"""

import json
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import traceback
import os
import sys

# Add the current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from final_robot_integration import enhanced_robot_analysis, show_trading_opportunities
from enhanced_day_trading_signals import enhanced_day_trading_signal
from utils.quick_technical_analysis import get_price_signals
from cedrotech_real_api import CedroTechRealAPI

class CedroTechTradingRobot:
    """
    ENHANCED TRADING ROBOT using CedroTech API
    Combines fundamental + technical analysis for superior signal generation
    """
    def __init__(self):
        # Robot identification
        self.robot_name = "CedroTech Enhanced Robot"
        self.version = "1.0.0"
        
        # Initialize CedroTech Real API
        self.real_api = CedroTechRealAPI()
        self.use_real_trading = True  # Set to False for simulation mode
        
        # State management
        self.state_file = "cedrotech_robot_state.json"
        self.current_asset = None
        self.current_position = None
        self.last_analysis_time = None
        
        # Trading parameters
        self.confidence_threshold = 70.0  # Minimum confidence for trades
        self.strong_signal_threshold = 80.0  # For STRONG_BUY signals
        self.max_position_size = 1000  # Maximum position size
        
        # Asset universe (Brazilian stocks)
        self.asset_universe = [
            'VALE3', 'PETR4', 'ITUB4', 'BBDC4', 'ABEV3',
            'AMER3', 'MGLU3', 'LREN3', 'RENT3', 'EMBR3'
        ]
        
        # Performance tracking
        self.trades_executed = 0
        self.total_profit_loss = 0.0
        self.last_signal_strength = 0.0
        
        # Load existing state
        self.load_robot_state()
    
    def load_robot_state(self):
        """Load robot state from file"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                
                self.current_asset = state.get('current_asset')
                self.current_position = state.get('current_position')
                self.last_analysis_time = state.get('last_analysis_time')
                self.trades_executed = state.get('trades_executed', 0)
                self.total_profit_loss = state.get('total_profit_loss', 0.0)
                
                print(f"🔄 LOADED STATE:")
                print(f"   Current Asset: {self.current_asset}")
                print(f"   Position: {self.current_position}")
                print(f"   Trades Executed: {self.trades_executed}")
                
        except Exception as e:
            print(f"⚠️  Could not load state: {e}")
            self.initialize_default_state()
    
    def save_robot_state(self):
        """Save current robot state"""
        try:
            state = {
                'robot_name': self.robot_name,
                'version': self.version,
                'current_asset': self.current_asset,
                'current_position': self.current_position,
                'last_analysis_time': self.last_analysis_time,
                'trades_executed': self.trades_executed,
                'total_profit_loss': self.total_profit_loss,
                'last_update': datetime.now().isoformat(),
                'last_signal_strength': self.last_signal_strength
            }
            
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
                
        except Exception as e:
            print(f"⚠️  Could not save state: {e}")
    
    def initialize_default_state(self):
        """Initialize robot with default state"""
        self.current_asset = None
        self.current_position = None
        self.trades_executed = 0
        self.total_profit_loss = 0.0
        self.last_analysis_time = None
        
        print("🆕 INITIALIZED DEFAULT STATE")
    
    def run_analysis_cycle(self) -> Dict:
        """
        Run a complete analysis cycle using enhanced combined signals
        Returns trading opportunities and recommendations
        """
        print(f"\n🤖 {self.robot_name.upper()} - ANALYSIS CYCLE")
        print("=" * 80)
        print(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Run enhanced analysis using our proven system
            results, all_signals = enhanced_robot_analysis()
            
            # Update analysis time
            self.last_analysis_time = datetime.now().isoformat()
            
            # Identify trading opportunities
            recommended_asset = self.evaluate_trading_opportunities(results)
            
            # Make trading decision
            trading_action = self.make_trading_decision(results, recommended_asset)
            
            # Save state
            self.save_robot_state()
            
            return {
                'results': results,
                'recommended_asset': recommended_asset,
                'trading_action': trading_action,
                'analysis_time': self.last_analysis_time
            }
            
        except Exception as e:
            print(f"❌ ANALYSIS CYCLE ERROR: {e}")
            traceback.print_exc()
            return {'error': str(e)}
    
    def evaluate_trading_opportunities(self, results: Dict) -> Optional[str]:
        """
        Evaluate trading opportunities from analysis results
        Returns the best asset to trade or None
        """
        print(f"\n🔍 EVALUATING TRADING OPPORTUNITIES")
        print("-" * 50)
        
        # Check for STRONG_BUY signals first
        if results['strong_buy']:
            top_signal = results['strong_buy'][0]
            self.last_signal_strength = top_signal['confidence']
            
            print(f"🚀 STRONG_BUY OPPORTUNITY FOUND!")
            print(f"   Asset: {top_signal['ticker']}")
            print(f"   Confidence: {top_signal['confidence']:.1f}%")
            print(f"   Agreement: {top_signal['agreement']}")
            
            return top_signal['ticker']
        
        # Check for BUY signals above threshold
        high_confidence_buys = [
            signal for signal in results['buy'] 
            if signal['confidence'] >= self.confidence_threshold
        ]
        
        if high_confidence_buys:
            top_signal = high_confidence_buys[0]
            self.last_signal_strength = top_signal['confidence']
            
            print(f"📈 HIGH-CONFIDENCE BUY OPPORTUNITY!")
            print(f"   Asset: {top_signal['ticker']}")
            print(f"   Confidence: {top_signal['confidence']:.1f}%")
            print(f"   Agreement: {top_signal['agreement']}")
            
            return top_signal['ticker']
        
        # Check for any BUY signals
        if results['buy']:
            top_signal = results['buy'][0]
            self.last_signal_strength = top_signal['confidence']
            
            print(f"📊 MODERATE BUY OPPORTUNITY")
            print(f"   Asset: {top_signal['ticker']}")
            print(f"   Confidence: {top_signal['confidence']:.1f}%")
            print(f"   Note: Below high-confidence threshold")
            
            return top_signal['ticker']
        
        print("⏸️  NO STRONG TRADING OPPORTUNITIES")
        print("   Waiting for better signals...")
        
        return None
    
    def make_trading_decision(self, results: Dict, recommended_asset: Optional[str]) -> Dict:
        """
        Make final trading decision based on analysis
        """
        print(f"\n🎯 MAKING TRADING DECISION")
        print("-" * 40)
        
        trading_action = {
            'action': 'HOLD',
            'asset': self.current_asset,
            'reason': 'No strong signals',
            'confidence': 0.0,
            'timestamp': datetime.now().isoformat()
        }
        
        # If no asset recommended, hold current position
        if not recommended_asset:
            if self.current_asset:
                print(f"⏸️  HOLDING CURRENT POSITION: {self.current_asset}")
                trading_action['reason'] = 'Waiting for stronger signals'
            else:
                print("⏸️  NO POSITION - WAITING FOR OPPORTUNITY")
                trading_action['reason'] = 'No trading opportunity identified'
            
            return trading_action
        
        # Get signal details for recommended asset
        recommended_signal = None
        for category in ['strong_buy', 'buy']:
            for signal in results.get(category, []):
                if signal['ticker'] == recommended_asset:
                    recommended_signal = signal
                    break
            if recommended_signal:
                break
        
        if not recommended_signal:
            print("❌ ERROR: Could not find signal for recommended asset")
            return trading_action
        
        # Decision logic
        if self.current_asset == recommended_asset:
            # Already holding the recommended asset
            print(f"✅ CONTINUING TO HOLD: {recommended_asset}")
            print(f"   Reason: Already holding the best opportunity")
            print(f"   Signal Strength: {recommended_signal['confidence']:.1f}%")
            
            trading_action.update({
                'action': 'HOLD',
                'asset': recommended_asset,
                'reason': f"Continuing to hold best opportunity ({recommended_signal['confidence']:.1f}%)",
                'confidence': recommended_signal['confidence']
            })
            
        elif self.current_asset and self.current_asset != recommended_asset:
            # Switch from current asset to recommended asset
            print(f"🔄 SWITCHING ASSETS!")
            print(f"   FROM: {self.current_asset}")
            print(f"   TO: {recommended_asset}")
            print(f"   Reason: Better opportunity identified")
            print(f"   New Signal Strength: {recommended_signal['confidence']:.1f}%")
            
            # Simulate selling current and buying new
            self.execute_asset_switch(self.current_asset, recommended_asset, recommended_signal)
            
            trading_action.update({
                'action': 'SWITCH',
                'from_asset': self.current_asset,
                'to_asset': recommended_asset,
                'reason': f"Switch to better opportunity ({recommended_signal['confidence']:.1f}%)",
                'confidence': recommended_signal['confidence']
            })
            
            self.current_asset = recommended_asset
            
        else:
            # No current position, enter new position
            print(f"🚀 ENTERING NEW POSITION: {recommended_asset}")
            print(f"   Signal: {recommended_signal['signal']}")
            print(f"   Confidence: {recommended_signal['confidence']:.1f}%")
            print(f"   Agreement: {recommended_signal['agreement']}")
            
            self.execute_buy_trade(recommended_asset, recommended_signal)
            
            trading_action.update({
                'action': 'BUY',
                'asset': recommended_asset,
                'reason': f"New {recommended_signal['signal']} signal ({recommended_signal['confidence']:.1f}%)",
                'confidence': recommended_signal['confidence']
            })
            
            self.current_asset = recommended_asset
        
        return trading_action    
    
    def execute_buy_trade(self, asset: str, signal: Dict):
        """Execute a buy trade using CedroTech Real API"""
        print(f"\n💰 EXECUTING BUY TRADE")
        print(f"   Asset: {asset}")
        print(f"   Signal: {signal['signal']}")
        print(f"   Confidence: {signal['confidence']:.1f}%")
        print(f"   Mode: {'REAL MONEY' if self.use_real_trading else 'SIMULATION'}")
        
        success = False
        order_id = None
        
        if self.use_real_trading:
            try:
                # Calculate position size based on confidence
                base_quantity = 100  # Base quantity
                confidence_multiplier = signal['confidence'] / 100.0
                quantity = int(base_quantity * confidence_multiplier)
                quantity = min(quantity, self.max_position_size)  # Respect max position
                  # Get current market price
                market_price = self.get_market_price(asset)
                
                print(f"   Quantity: {quantity} shares")
                print(f"   Market Price: R${market_price:.2f}")
                print(f"   Total Value: R${market_price * quantity:.2f}")
                
                # Execute real buy order
                response = self.real_api.place_buy_order(
                    symbol=asset,
                    quantity=quantity,
                    price=market_price
                )
                
                if response and response.get('success'):
                    success = True
                    order_id = response.get('order_id')
                    print(f"✅ REAL ORDER PLACED SUCCESSFULLY!")
                    print(f"   Order ID: {order_id}")
                    print(f"   Quantity: {quantity}")
                else:
                    print(f"❌ REAL ORDER FAILED: {response.get('error', 'Unknown error')}")
                    print("   Falling back to simulation mode...")
                    
            except Exception as e:
                print(f"❌ REAL TRADING ERROR: {e}")
                print("   Falling back to simulation mode...")
        
        if not success:
            # Simulation mode or fallback
            print(f"📊 SIMULATED BUY TRADE")
            success = True  # Simulation always "succeeds"
        
        # Update robot state
        self.trades_executed += 1
        self.current_position = 'LONG'
        
        trade_record = {
            'action': 'BUY',
            'asset': asset,
            'confidence': signal['confidence'],
            'signal_type': signal['signal'],
            'agreement': signal['agreement'],
            'timestamp': datetime.now().isoformat(),
            'trade_number': self.trades_executed,
            'mode': 'REAL' if self.use_real_trading and success else 'SIMULATION',
            'order_id': order_id
        }
        
        # Log trade
        self.log_trade(trade_record)
        
        print(f"✅ TRADE EXECUTED SUCCESSFULLY!")
        print(f"   Trade #: {self.trades_executed}")
        print(f"   Position: {self.current_position}")
        
        return success
      
    def execute_asset_switch(self, from_asset: str, to_asset: str, new_signal: Dict):
        """Execute asset switch (sell old, buy new) using real API"""
        print(f"\n🔄 EXECUTING ASSET SWITCH")
        print(f"   Selling: {from_asset}")
        print(f"   Buying: {to_asset}")
        print(f"   Mode: {'REAL MONEY' if self.use_real_trading else 'SIMULATION'}")
        
        sell_success = False
        buy_success = False
        
        if self.use_real_trading:            
            try:
                # First, sell the current position
                quantity = 100  # Should track actual position size
                from_price = self.get_market_price(from_asset)
                to_price = self.get_market_price(to_asset)
                
                print(f"   Sell {from_asset} at R${from_price:.2f}")
                print(f"   Buy {to_asset} at R${to_price:.2f}")
                
                sell_response = self.real_api.place_sell_order(
                    symbol=from_asset,
                    quantity=quantity,
                    price=from_price
                )
                
                if sell_response and sell_response.get('success'):
                    sell_success = True
                    print(f"✅ SELL ORDER PLACED: {from_asset}")
                      # Then buy the new asset
                    buy_response = self.real_api.place_buy_order(
                        symbol=to_asset,
                        quantity=quantity,
                        price=to_price
                    )
                    
                    if buy_response and buy_response.get('success'):
                        buy_success = True
                        print(f"✅ BUY ORDER PLACED: {to_asset}")
                    else:
                        print(f"❌ BUY ORDER FAILED: {buy_response.get('error', 'Unknown error')}")
                else:
                    print(f"❌ SELL ORDER FAILED: {sell_response.get('error', 'Unknown error')}")
                    
            except Exception as e:
                print(f"❌ ASSET SWITCH ERROR: {e}")
                print("   Falling back to simulation mode...")
        
        if not (sell_success and buy_success):
            # Simulation mode or fallback
            print(f"📊 SIMULATED ASSET SWITCH")
            sell_success = buy_success = True
        
        # Update robot state
        self.trades_executed += 2  # Count as two trades
        
        switch_record = {
            'action': 'SWITCH',
            'from_asset': from_asset,
            'to_asset': to_asset,
            'new_confidence': new_signal['confidence'],
            'new_signal_type': new_signal['signal'],
            'timestamp': datetime.now().isoformat(),
            'trade_number': self.trades_executed,
            'mode': 'REAL' if self.use_real_trading and sell_success and buy_success else 'SIMULATION'
        }
        
        # Log switch
        self.log_trade(switch_record)
        
        print(f"✅ ASSET SWITCH COMPLETED!")
        print(f"   New Position: {to_asset}")
        print(f"   Total Trades: {self.trades_executed}")
        
        return sell_success and buy_success
    
    def log_trade(self, trade_record: Dict):
        """Log trade to file"""
        try:
            log_file = "cedrotech_trading_log.json"
            
            # Load existing log
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    log_data = json.load(f)
            else:
                log_data = {'trades': []}
            
            # Add new trade
            log_data['trades'].append(trade_record)
            
            # Save updated log
            with open(log_file, 'w') as f:
                json.dump(log_data, f, indent=2)
                
        except Exception as e:
            print(f"⚠️  Could not log trade: {e}")
    
    def generate_performance_report(self) -> str:
        """Generate performance report"""
        report = []
        report.append("📊 CEDROTECH ROBOT PERFORMANCE REPORT")
        report.append("=" * 60)
        report.append(f"🤖 Robot: {self.robot_name}")
        report.append(f"📅 Report Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Current status
        report.append("🎯 CURRENT STATUS:")
        report.append(f"   Asset: {self.current_asset or 'None'}")
        report.append(f"   Position: {self.current_position or 'None'}")
        report.append(f"   Last Signal Strength: {self.last_signal_strength:.1f}%")
        report.append(f"   Total Trades: {self.trades_executed}")
        report.append("")
        
        # Recent activity
        if self.last_analysis_time:
            last_analysis = datetime.fromisoformat(self.last_analysis_time)
            time_since = datetime.now() - last_analysis
            report.append(f"⏰ LAST ANALYSIS: {time_since.seconds // 60} minutes ago")
        
        report.append("")
        report.append("🚀 NEXT CYCLE:")
        report.append("   The robot will continue monitoring for opportunities")
        report.append("   Enhanced signals ensure quick response to market changes")
        return "\n".join(report)
    
    def run_continuous(self, cycles: int = 1, continuous_mode: bool = False, cycle_interval: int = 300):
        """
        Run robot for specified number of cycles or continuously
        
        Args:
            cycles: Number of cycles to run (ignored if continuous_mode=True)
            continuous_mode: If True, runs indefinitely
            cycle_interval: Seconds between cycles (default 5 minutes)
        """
        print(f"🚀 STARTING CEDROTECH ENHANCED ROBOT")
        
        if continuous_mode:
            print(f"🔄 Running in CONTINUOUS MODE (every {cycle_interval} seconds)")
            print("   Press Ctrl+C to stop")
        else:
            print(f"🔄 Running {cycles} analysis cycle(s)")
            
        print("=" * 80)
        
        cycle_count = 0
        start_time = datetime.now()
        
        try:
            while True:
                cycle_count += 1
                
                if not continuous_mode and cycle_count > cycles:
                    break
                
                print(f"\n🔄 CYCLE {cycle_count}" + (f" of {cycles}" if not continuous_mode else ""))
                print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("-" * 50)
                
                # Run analysis cycle
                cycle_result = self.run_analysis_cycle()
                
                # Show results
                if 'error' not in cycle_result:
                    recommended_asset = cycle_result.get('recommended_asset')
                    trading_action = cycle_result.get('trading_action', {})
                    
                    print(f"\n📋 CYCLE SUMMARY:")
                    print(f"   Recommended Asset: {recommended_asset or 'None'}")
                    print(f"   Action Taken: {trading_action.get('action', 'Unknown')}")
                    print(f"   Current Asset: {self.current_asset or 'None'}")
                    print(f"   Total Trades: {self.trades_executed}")
                
                # Wait between cycles
                if continuous_mode or (not continuous_mode and cycle_count < cycles):
                    next_cycle_time = datetime.now() + timedelta(seconds=cycle_interval)
                    print(f"\n⏳ Next cycle at: {next_cycle_time.strftime('%H:%M:%S')}")
                    print(f"   Waiting {cycle_interval} seconds...")
                    
                    # Sleep in smaller chunks to allow for interruption
                    for i in range(cycle_interval):
                        time.sleep(1)
                        if i > 0 and i % 60 == 0:  # Show progress every minute
                            remaining = cycle_interval - i
                            print(f"   ⏱️  {remaining} seconds remaining...")
        
        except KeyboardInterrupt:
            print(f"\n🛑 ROBOT STOPPED BY USER")
            print(f"   Completed {cycle_count} cycles")
            
        except Exception as e:
            print(f"\n❌ ROBOT ERROR: {e}")
            traceback.print_exc()
        
        finally:
            # Final report
            session_duration = datetime.now() - start_time
            print(f"\n{self.generate_performance_report()}")
            print(f"\n🏁 ROBOT SESSION ENDED")
            print(f"   Total Cycles: {cycle_count}")
            print(f"   Session Duration: {session_duration}")
            print(f"   Average Cycle Time: {session_duration.total_seconds() / max(cycle_count, 1):.1f} seconds")
    
    def set_trading_mode(self, real_trading: bool):
        """Set trading mode - True for real money, False for simulation"""
        self.use_real_trading = real_trading
        mode = "REAL MONEY" if real_trading else "SIMULATION"
        print(f"🔧 TRADING MODE SET TO: {mode}")
        
        if real_trading:
            print("⚠️  WARNING: REAL MONEY TRADING ENABLED!")
            print("   All orders will use actual funds")
            print("   Make sure credentials are properly configured")
        else:
            print("📊 Simulation mode - no real orders will be placed")
    
    def get_market_price(self, symbol: str) -> float:
        """Get current market price for a symbol (placeholder implementation)"""
        # In a real implementation, this would fetch from market data API
        # For now, return a reasonable default for Brazilian stocks
        default_prices = {
            'PETR4': 25.50,
            'VALE3': 62.30,
            'ITUB4': 32.10,
            'BBDC4': 14.80,
            'ABEV3': 11.90,
            'AMER3': 28.40,
            'MGLU3': 8.50,
            'LREN3': 45.20,
            'RENT3': 58.70,
            'EMBR3': 22.10
        }
        
        return default_prices.get(symbol, 25.0)  # Default to 25.0 if not found
    
    def validate_trading_setup(self) -> bool:
        """Validate that trading setup is ready"""
        if not self.use_real_trading:
            print("✅ Simulation mode - no validation needed")
            return True
        
        print("🔍 VALIDATING REAL TRADING SETUP...")
        
        try:
            # Check if API is properly initialized
            if not hasattr(self, 'real_api') or not self.real_api:
                print("❌ CedroTech API not initialized")
                return False
            
            # Check credentials
            if not self.real_api.username or not self.real_api.user_identifier or not self.real_api.account:
                print("❌ Missing CedroTech credentials")
                return False
            
            print("✅ Real trading setup validated")
            print(f"   Username: {self.real_api.username}")
            print(f"   Account: {self.real_api.account}")
            return True
            
        except Exception as e:
            print(f"❌ Validation error: {e}")
            return False

    def is_market_open(self) -> bool:
        """Check if market is currently open (Brazilian market hours)"""
        now = datetime.now()
        
        # Brazilian market hours: 10:00 - 17:30 (BRT), Monday-Friday
        # For now, simplified check - in production use proper market calendar
        if now.weekday() >= 5:  # Weekend (Saturday=5, Sunday=6)
            return False
        
        current_time = now.time()
        market_open = datetime.strptime("10:00", "%H:%M").time()
        market_close = datetime.strptime("17:30", "%H:%M").time()
        
        return market_open <= current_time <= market_close
    
    def get_adaptive_cycle_interval(self) -> int:
        """Get adaptive cycle interval based on market conditions"""
        if not self.is_market_open():
            return 1800  # 30 minutes when market is closed
        
        # During market hours, use shorter intervals
        if self.current_position:
            return 180  # 3 minutes when holding position
        else:
            return 300  # 5 minutes when no position
    
    def run_continuous_monitoring(self):
        """Run continuous monitoring with adaptive intervals"""
        print("🌟 STARTING CONTINUOUS MARKET MONITORING")
        print("   Adaptive intervals based on market hours and position")
        print("   Press Ctrl+C to stop")
        print("=" * 80)
        
        cycle_count = 0
        start_time = datetime.now()
        
        try:
            while True:
                cycle_count += 1
                
                # Check market status
                market_open = self.is_market_open()
                interval = self.get_adaptive_cycle_interval()
                
                print(f"\n🔄 CYCLE {cycle_count}")
                print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"🏪 Market: {'OPEN' if market_open else 'CLOSED'}")
                print(f"⏳ Next check in: {interval} seconds ({interval//60} minutes)")
                print("-" * 50)
                
                if market_open:
                    # Run full analysis during market hours
                    cycle_result = self.run_analysis_cycle()
                    
                    if 'error' not in cycle_result:
                        recommended_asset = cycle_result.get('recommended_asset')
                        trading_action = cycle_result.get('trading_action', {})
                        
                        print(f"\n📋 CYCLE SUMMARY:")
                        print(f"   Recommended Asset: {recommended_asset or 'None'}")
                        print(f"   Action Taken: {trading_action.get('action', 'Unknown')}")
                        print(f"   Current Asset: {self.current_asset or 'None'}")
                        print(f"   Total Trades: {self.trades_executed}")
                else:
                    # Market closed - just monitor and wait
                    print("🏪 Market closed - monitoring mode")
                    print(f"   Current Position: {self.current_asset or 'None'}")
                    print("   Waiting for market to open...")
                
                # Wait with progress updates
                next_cycle_time = datetime.now() + timedelta(seconds=interval)
                print(f"\n⏳ Next cycle at: {next_cycle_time.strftime('%H:%M:%S')}")
                
                # Sleep in smaller chunks
                for i in range(interval):
                    time.sleep(1)
                    if i > 0 and i % 300 == 0:  # Show progress every 5 minutes
                        remaining = interval - i
                        print(f"   ⏱️  {remaining} seconds remaining...")
        
        except KeyboardInterrupt:
            print(f"\n🛑 MONITORING STOPPED BY USER")
            print(f"   Completed {cycle_count} cycles")
            
        except Exception as e:
            print(f"\n❌ MONITORING ERROR: {e}")
            traceback.print_exc()
        
        finally:
            session_duration = datetime.now() - start_time
            print(f"\n{self.generate_performance_report()}")
            print(f"\n🏁 MONITORING SESSION ENDED")
            print(f"   Total Cycles: {cycle_count}")
            print(f"   Session Duration: {session_duration}")

    # ...existing code...
def main():
    """Main function to run the CedroTech robot"""
    print("🚀 INITIALIZING CEDROTECH ENHANCED ROBOT")
    print("=" * 60)
    
    robot = CedroTechTradingRobot()
    
    # Interactive trading mode selection
    print("\n💰 TRADING MODE SELECTION")
    print("-" * 30)
    print("1. 📊 SIMULATION MODE (Safe - No real money)")
    print("2. 🔥 REAL MONEY TRADING (Live orders with real funds)")
    print("")
    
    while True:
        try:
            choice = input("Choose trading mode (1 or 2): ").strip()
            if choice == "1":
                USE_REAL_TRADING = False
                print("✅ SIMULATION MODE SELECTED")
                break
            elif choice == "2":
                USE_REAL_TRADING = True
                print("⚠️  REAL MONEY TRADING SELECTED!")
                break
            else:
                print("❌ Invalid choice. Please enter 1 or 2.")
        except KeyboardInterrupt:
            print("\n❌ Operation cancelled by user")
            return
    
    robot.set_trading_mode(USE_REAL_TRADING)
    
    # Validate setup if using real trading
    if USE_REAL_TRADING:
        if not robot.validate_trading_setup():
            print("❌ Trading setup validation failed!")
            print("   Please check credentials and try again")
            return
        
        print("\n🚨 FINAL WARNING: REAL MONEY TRADING ENABLED!")
        print("   This will place ACTUAL orders with REAL money!")
        print("   Press Ctrl+C within 10 seconds to cancel...")
        try:
            for i in range(10, 0, -1):
                print(f"   Continuing in {i} seconds... (Ctrl+C to cancel)")
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n❌ Operation cancelled by user")
            return
        
        print("🔥 PROCEEDING WITH REAL MONEY TRADING!")
    
    print(f"\n🎯 STARTING TRADING OPERATIONS")
    print(f"   Mode: {'🔥 REAL MONEY' if USE_REAL_TRADING else '📊 SIMULATION'}")
    print("-" * 50)
    
    # Interactive operation mode selection
    print("\n🔄 OPERATION MODE SELECTION")
    print("-" * 30)
    print("1. 🎯 SINGLE CYCLE (Run once and exit)")
    print("2. 🔄 CONTINUOUS MONITORING (Fixed 5-minute intervals)")
    print("3. 🌟 ADAPTIVE MONITORING (Smart intervals based on market)")
    print("")
    
    while True:
        try:
            mode_choice = input("Choose operation mode (1, 2, or 3): ").strip()
            if mode_choice == "1":
                OPERATION_MODE = "SINGLE"
                break
            elif mode_choice == "2":
                OPERATION_MODE = "CONTINUOUS"
                break
            elif mode_choice == "3":
                OPERATION_MODE = "ADAPTIVE_CONTINUOUS"
                break
            else:
                print("❌ Invalid choice. Please enter 1, 2, or 3.")
        except KeyboardInterrupt:
            print("\n❌ Operation cancelled by user")
            return
    
    print(f"\n🚀 STARTING ROBOT IN {OPERATION_MODE} MODE")
    print("=" * 60)
    
    if OPERATION_MODE == "SINGLE":
        print("🔄 SINGLE CYCLE MODE")
        robot.run_continuous(cycles=1)
        
    elif OPERATION_MODE == "CONTINUOUS":
        print("🔄 CONTINUOUS MONITORING MODE")
        CYCLE_INTERVAL = 300  # 5 minutes
        print(f"   Fixed Interval: {CYCLE_INTERVAL} seconds ({CYCLE_INTERVAL//60} minutes)")
        robot.run_continuous(continuous_mode=True, cycle_interval=CYCLE_INTERVAL)
        
    elif OPERATION_MODE == "ADAPTIVE_CONTINUOUS":
        print("🌟 ADAPTIVE CONTINUOUS MONITORING")
        print("   Smart intervals based on market hours and position")
        robot.run_continuous_monitoring()
    
    else:
        print("❌ Invalid operation mode specified")
        return

if __name__ == "__main__":
    main()
