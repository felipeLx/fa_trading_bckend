#!/usr/bin/env python3
"""
Options Trading Robot - Specialized for Brazilian Options Market
Built on proven robot.py architecture but optimized for options trading

Key Differences from Stock Robot:
- 100% CedroTech API (real-time quotes required)
- Options-specific risk management (1% max per trade)
- Time decay monitoring (Theta)
- Bid/ask spread validation
- Greeks analysis integration
- Expiry date management
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import os
from dotenv import load_dotenv
from utils.cedrotech_api_correct import CedroTechAPICorrect
from utils.balance_manager import BalanceManager
from cedrotech_options_api import CedroTechOptionsAPI
import json
from datetime import datetime, timedelta
import math

load_dotenv()

STATE_FILE = 'options_robot_state.json'

def send_email(subject, body):
    """Send an email notification."""
    sender_email = os.environ.get('GMAIL', '')  
    sender_password = os.environ.get('PASS', '')
    receiver_email = os.environ.get('GMAIL', '') 

    if not sender_email or not sender_password:
        print(f"Email notification: {subject} - {body}")
        return

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)
        server.quit()
        print(f"✅ Email sent: {subject}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

# OPTIONS TRADING CONFIGURATION
MARKET_OPEN_TIME = "09:00"  # 9:00 AM Brazil time
MARKET_CLOSE_TIME = "17:30"  # 5:30 PM Brazil time
FORCE_CLOSE_TIME = "16:30"  # Force close 1 hour before market close (options decay fast)
MAX_DAILY_OPTIONS_TRADES = 2  # Conservative limit for options
DAILY_LOSS_LIMIT = 0.03  # Stop trading if daily loss exceeds 3% (more conservative)
MAX_RISK_PER_TRADE = 0.01  # Only risk 1% per options trade
MIN_OPTION_PRICE = 0.05  # Don't trade options below R$0.05
MAX_BID_ASK_SPREAD = 0.15  # Max 15% bid/ask spread
MIN_OPEN_INTEREST = 1000  # Minimum open interest required
MIN_VOLUME = 10  # Minimum daily volume required

# TARGET OPTIONS (from analysis)
# Note: This will be dynamically updated by options_filter_analysis.py
TRADEABLE_OPTIONS = [
    {
        'symbol': 'valeg565w2',
        'score': 65,
        'open_interest': 14500,
        'underlying': 'VALE3'
    },
    {
        'symbol': 'valeg545w2', 
        'score': 50,
        'open_interest': 4400,
        'underlying': 'VALE3'
    }
]

def run_options_filter_analysis():
    """
    Run options filter analysis to get today's best options
    
    Returns:
        list: List of best tradeable options for today
    """
    try:
        print("🔍 Running daily options discovery and analysis...")
        
        # Import and run the daily options discovery
        import subprocess
        import sys
        
        # Run daily options discovery and analysis
        result = subprocess.run([
            sys.executable, 'daily_options_discovery.py'
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode != 0:
            print(f"⚠️ Daily options discovery failed: {result.stderr}")
            print("📋 Using default options list...")
            return TRADEABLE_OPTIONS
        
        # Load the analysis results
        analysis_file = 'tradeable_options_analysis.json'
        if os.path.exists(analysis_file):
            with open(analysis_file, 'r') as f:
                analysis_results = json.load(f)
            
            # Extract top 5 tradeable options
            tradeable_options = analysis_results.get('tradeable_options', [])
            
            if tradeable_options:
                # Convert to robot format
                robot_options = []
                for option in tradeable_options[:8]:  # Top 8 options for more diversity
                    option_data = option.get('option_data', {})
                    
                    # Extract underlying from the option data
                    underlying = option_data.get('underlying', 'UNKNOWN')
                    
                    robot_option = {
                        'symbol': option.get('symbol', ''),
                        'score': option.get('quality_score', 0),
                        'open_interest': option_data.get('open_interest', 0),
                        'underlying': underlying,
                        'rating': option.get('overall_rating', 'UNKNOWN'),
                        'liquidity_rating': option.get('liquidity_rating', 'UNKNOWN'),
                        'volume': option_data.get('volume', 0),
                        'bid': option_data.get('bid', 0),
                        'ask': option_data.get('ask', 0)
                    }
                    robot_options.append(robot_option)
                
                print(f"✅ Found {len(robot_options)} tradeable options from daily analysis")
                print("🏆 Top options for today:")
                for i, opt in enumerate(robot_options[:5]):  # Show top 5
                    print(f"   {i+1}. {opt['symbol']} ({opt['underlying']}) - Score: {opt['score']}, Rating: {opt['rating']}")
                
                return robot_options
            else:
                print("⚠️ No tradeable options found in daily analysis")
                print("📋 Using default options list...")
                return TRADEABLE_OPTIONS
        else:
            print(f"⚠️ Analysis file {analysis_file} not found")
            print("📋 Using default options list...")
            return TRADEABLE_OPTIONS
            
    except Exception as e:
        print(f"❌ Error running daily options discovery: {e}")
        print("📋 Using default options list...")
        return TRADEABLE_OPTIONS

def initialize_options_api(paper_trading=True):
    """Initialize CedroTech Options API for live trading"""
    try:
        # Standard API for orders
        api = CedroTechAPICorrect(paper_trading=paper_trading)
        
        # Options-specific API for quotes and analysis
        options_api = CedroTechOptionsAPI()
        
        print(f"✅ Options Trading APIs initialized successfully")
        print(f"   Mode: {'PAPER TRADING' if paper_trading else 'LIVE TRADING'}")
        return api, options_api
    except Exception as e:
        print(f"❌ Failed to initialize Options APIs: {e}")
        return None, None

def load_options_state():
    """Load options robot state"""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                state = json.load(f)
                
                # Check if we need to reset for a new trading day
                if should_reset_for_new_day(state):
                    print("🔄 New options trading day detected - resetting state...")
                    state = reset_options_state()
                    save_options_state(state)
                
                return state
        except Exception as e:
            print(f"Failed to load options state: {e}")
    return reset_options_state()

def should_reset_for_new_day(state):
    """Check if we should reset state for a new trading day"""
    last_analysis = state.get('last_analysis_date')
    if not last_analysis:
        return True
    try:
        last_date = datetime.strptime(last_analysis, '%Y-%m-%d %H:%M:%S')
        today = datetime.now()
        
        if last_date.date() < today.date():
            return True
            
        # Reset if more than 18 hours have passed
        hours_diff = (today - last_date).total_seconds() / 3600
        if hours_diff > 18:
            return True
            
    except (ValueError, TypeError):
        return True
    
    return False

def reset_options_state():
    """Reset the options trading state for a new day"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Initialize balance manager to get current balance
    balance_manager = BalanceManager()
    balance_info = balance_manager.get_current_balance()
    current_balance = balance_info['balance']
    
    return {
        'holding_option': None,
        'option_contracts': 0,
        'entry_price': None,
        'stop_loss': None,
        'take_profit': None,
        'expiry_date': None,
        'last_analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'trading_date': today,
        'daily_trades_count': 0,
        'daily_initial_balance': current_balance,
        'account_balance': current_balance,
        'total_premium_paid': 0,
        'daily_pnl': 0
    }

def save_options_state(state):
    """Save options robot state"""
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        print(f"Failed to save options state: {e}")

def validate_option_tradeable(option_symbol, options_api):
    """
    Validate if an option is currently tradeable
    
    Args:
        option_symbol (str): Option symbol to validate
        options_api: CedroTech Options API instance
        
    Returns:
        dict: Validation result with tradeable status and metrics
    """
    try:
        print(f"🔍 Validating option: {option_symbol}")
        
        # Get current option quote using get_asset_info (correct CedroTech API method)
        if not options_api.authenticated:
            if not options_api.authenticate():
                return {'tradeable': False, 'reason': 'API authentication failed'}
        
        quote_result = options_api.get_asset_info(option_symbol)
        if not quote_result.get('success'):
            return {'tradeable': False, 'reason': 'No quote available'}
        
        quote = quote_result.get('data', {})
        
        # Extract quote data - match CedroTech API response format
        bid = float(quote.get('bid', quote.get('bidPrice', 0)))
        ask = float(quote.get('ask', quote.get('askPrice', 0)))
        last_trade = float(quote.get('lastTrade', quote.get('last', quote.get('price', 0))))
        volume = int(quote.get('volume', quote.get('volumeAmount', 0)))
        open_interest = int(quote.get('openInterest', quote.get('interest', 0)))
        
        # Validation checks
        checks = {
            'has_bid_ask': bid > 0 and ask > 0,
            'spread_acceptable': False,
            'price_acceptable': last_trade >= MIN_OPTION_PRICE,
            'volume_sufficient': volume >= MIN_VOLUME,
            'open_interest_sufficient': open_interest >= MIN_OPEN_INTEREST
        }
        
        # Calculate spread if bid/ask available
        if checks['has_bid_ask']:
            spread_percent = ((ask - bid) / ask) * 100
            checks['spread_acceptable'] = spread_percent <= (MAX_BID_ASK_SPREAD * 100)
        
        # Determine if tradeable
        tradeable = all([
            checks['has_bid_ask'],
            checks['spread_acceptable'], 
            checks['price_acceptable'],
            checks['volume_sufficient'],
            checks['open_interest_sufficient']
        ])
        
        result = {
            'tradeable': tradeable,
            'bid': bid,
            'ask': ask,
            'last_trade': last_trade,
            'volume': volume,
            'open_interest': open_interest,
            'spread_percent': ((ask - bid) / ask) * 100 if bid > 0 and ask > 0 else 100,
            'checks': checks
        }
        
        if not tradeable:
            failed_checks = [k for k, v in checks.items() if not v]
            result['reason'] = f"Failed checks: {', '.join(failed_checks)}"
        
        return result
        
    except Exception as e:
        print(f"❌ Error validating option {option_symbol}: {e}")
        return {'tradeable': False, 'reason': f'Validation error: {e}'}

def calculate_option_position_size(account_balance, risk_per_trade, option_price):
    """
    Calculate conservative position size for options
    
    Args:
        account_balance (float): Current account balance
        risk_per_trade (float): Risk percentage (0.01 = 1%)
        option_price (float): Current option price
        
    Returns:
        int: Number of contracts to buy (conservative)
    """
    try:
        # Calculate maximum risk amount
        max_risk = account_balance * risk_per_trade
        
        # For options, we risk the entire premium paid
        max_contracts = int(max_risk / option_price)
        
        # Conservative limits
        max_contracts = min(max_contracts, 5)  # Never more than 5 contracts
        max_contracts = max(max_contracts, 1)  # Always at least 1 contract
        
        return max_contracts
        
    except Exception as e:
        print(f"❌ Error calculating position size: {e}")
        return 1

def check_option_expiry(option_symbol):
    """
    Check if option is close to expiry
    
    Args:
        option_symbol (str): Option symbol
        
    Returns:
        dict: Expiry information
    """
    try:
        # TODO: Parse expiry date from option symbol or API
        # For now, return conservative estimate
        return {
            'days_to_expiry': 7,  # Assume 1 week
            'should_close': False  # Close if < 2 days
        }
    except Exception as e:
        print(f"❌ Error checking expiry for {option_symbol}: {e}")
        return {'days_to_expiry': 0, 'should_close': True}

def monitor_and_trade_options(account_balance, paper_trading=True):
    """
    Main options trading loop - specialized for options market
    """
    print("="*80)
    print("🎯 OPTIONS TRADING ROBOT - BRAZILIAN MARKET SPECIALIST")
    print("="*80)
    
    # Initialize APIs
    api, options_api = initialize_options_api(paper_trading=paper_trading)
    if not api or not options_api:
        print("❌ Cannot start options trading without API connections")
        return
    
    # Initialize Balance Manager
    balance_manager = BalanceManager(api=api)
    
    # Load state
    state = load_options_state()
      # Initialize daily tracking if new day
    today = datetime.now().strftime('%Y-%m-%d')
    if state.get('trading_date') != today:
        balance_info = balance_manager.get_current_balance()
        current_balance = balance_info['balance']
        
        # Run daily options analysis to get best options for today
        print("🎯 Getting today's best options from filter analysis...")
        daily_options = run_options_filter_analysis()
        
        state['trading_date'] = today
        state['daily_trades_count'] = 0
        state['daily_initial_balance'] = current_balance
        state['account_balance'] = current_balance
        state['daily_pnl'] = 0
        state['daily_options_list'] = daily_options  # Store today's options
        save_options_state(state)
        
        print(f"🌅 New options trading day: {today}")
        print(f"💰 Starting balance: R${current_balance:.2f}")
        print(f"🎯 Today's target options: {len(daily_options)} options loaded")
    else:
        # Use stored options for the day
        daily_options = state.get('daily_options_list', TRADEABLE_OPTIONS)
        
    print(f"📊 Daily Limits: Max {MAX_DAILY_OPTIONS_TRADES} trades, Max {DAILY_LOSS_LIMIT*100}% loss")
    print(f"🎯 Target Options: {len(daily_options)} pre-analyzed options")
    print(f"🔗 Trading Mode: {'PAPER' if paper_trading else 'LIVE'}")
    
    while True:
        current_time = datetime.now().strftime("%H:%M")
        
        # Market hours check
        if not is_market_hours():
            print(f"🕐 Market closed ({current_time}). Options robot stopped.")
            break
        
        # Force close check (more aggressive for options)
        if should_force_close_positions():
            print("⚠️ Approaching market close - force closing options positions")
            # TODO: Implement force close logic
            break
        
        # Daily limits check
        if state.get('daily_trades_count', 0) >= MAX_DAILY_OPTIONS_TRADES:
            print(f"📈 Daily options trade limit reached ({MAX_DAILY_OPTIONS_TRADES})")
            time.sleep(300)
            continue
        
        # Daily loss limit check
        current_pnl_percent = (state.get('daily_pnl', 0) / state.get('daily_initial_balance', 1000)) * 100
        if current_pnl_percent <= -(DAILY_LOSS_LIMIT * 100):
            print(f"🛑 Daily loss limit reached ({DAILY_LOSS_LIMIT*100}%). Stopping options trading.")
            break
        
        holding_option = state.get('holding_option')
        
        if holding_option is None:
            print("\n🔍 Scanning for options trading opportunities...")
              # Analyze each pre-qualified option
            best_option = None
            best_score = 0
            
            for option_info in daily_options:
                symbol = option_info['symbol']
                print(f"\n📊 Analyzing {symbol}...")
                
                # Validate current tradeability
                validation = validate_option_tradeable(symbol, options_api)
                
                if validation['tradeable']:
                    print(f"✅ {symbol} is tradeable:")
                    print(f"   Bid/Ask: {validation['bid']:.2f}/{validation['ask']:.2f}")
                    print(f"   Spread: {validation['spread_percent']:.1f}%")
                    print(f"   Volume: {validation['volume']}")
                    print(f"   Open Interest: {validation['open_interest']:,}")
                    print(f"   Pre-analysis Score: {option_info['score']}")
                    print(f"   Rating: {option_info.get('rating', 'N/A')}")
                    
                    # Score this option (combine pre-analysis score with current metrics)
                    current_score = option_info['score']
                    
                    # Bonus for tight spreads and good volume
                    if validation['spread_percent'] < 5:
                        current_score += 10
                    if validation['volume'] > 50:
                        current_score += 5
                    
                    # Bonus for excellent ratings from analysis
                    if option_info.get('rating') == 'EXCELLENT':
                        current_score += 15
                    elif option_info.get('rating') == 'GOOD':
                        current_score += 10
                    
                    if current_score > best_score:
                        best_score = current_score
                        best_option = {
                            'symbol': symbol,
                            'score': current_score,
                            'validation': validation,
                            'underlying': option_info['underlying'],
                            'rating': option_info.get('rating', 'N/A')
                        }
                else:
                    print(f"❌ {symbol} not tradeable: {validation['reason']}")
            
            if best_option:
                print(f"\n🎯 Selected option: {best_option['symbol']} (Score: {best_option['score']})")
                  # Calculate position size
                option_price = best_option['validation']['ask']  # Use ask price for buying
                contracts = calculate_option_position_size(
                    state['account_balance'], 
                    MAX_RISK_PER_TRADE, 
                    option_price
                )
                  # Validate trade affordability
                total_cost = contracts * option_price
                affordability_check = balance_manager.validate_trade_affordability(
                    best_option['symbol'], contracts, option_price
                )
                if not affordability_check['affordable']:
                    print(f"❌ Insufficient balance for options trade: {affordability_check['message']}")
                    print("⏳ Waiting 5 minutes before next scan...")
                    time.sleep(300)
                    continue
                
                print(f"📦 Position size: {contracts} contracts at R${option_price:.2f}")
                print(f"💰 Total premium: R${contracts * option_price:.2f}")
                
                # Execute buy order via CedroTech API
                print(f"📤 Executing OPTIONS BUY order via CedroTech API...")
                order_result = api.place_buy_order(
                    ticker=best_option['symbol'],
                    quantity=contracts,
                    order_type="MARKET"
                )
                
                if order_result.get('success'):
                    print(f"✅ Options buy order executed: {order_result.get('order_id')}")
                      # Send email notification
                    send_email(
                        "OPTIONS TRADE - BUY", 
                        f"Bought {contracts} contracts of {best_option['symbol']} at R${option_price:.2f}\n"
                        f"Total premium paid: R${contracts * option_price:.2f}\n"
                        f"Underlying: {best_option['underlying']}\n"
                        f"Final Score: {best_option['score']}\n"
                        f"Analysis Rating: {best_option.get('rating', 'N/A')}\n"
                        f"Current Spread: {best_option['validation']['spread_percent']:.1f}%"
                    )
                    
                    # Update balance after successful buy order
                    balance_manager.update_balance_after_trade(
                        trade_type='buy',
                        ticker=best_option['symbol'],
                        price=option_price,
                        volume=contracts
                    )
                    
                    # Update state with successful trade
                    state['holding_option'] = best_option['symbol']
                    state['option_contracts'] = contracts
                    state['entry_price'] = option_price
                    state['total_premium_paid'] = contracts * option_price
                    
                    # Update balance in state
                    current_balance_info = balance_manager.get_current_balance()
                    state['account_balance'] = current_balance_info['balance']
                    
                    save_options_state(state)
                    
                    print(f"💰 Updated Balance: R${current_balance_info['balance']:.2f}")
                else:
                    print(f"❌ Options buy order failed: {order_result.get('error')}")
                    continue  # Skip to next iteration
                
            else:
                print("❌ No tradeable options found at this time")
                print("⏳ Waiting 5 minutes before next scan...")
                time.sleep(300)
                continue
                
        else:
            print(f"\n👀 Monitoring option position: {holding_option}")
            
            # Check current option value
            validation = validate_option_tradeable(holding_option, options_api)
            
            if validation['tradeable']:
                current_bid = validation['bid']
                current_value = state['option_contracts'] * current_bid
                entry_value = state['total_premium_paid']
                pnl = current_value - entry_value
                pnl_percent = (pnl / entry_value) * 100
                
                print(f"📊 Current position:")
                print(f"   Contracts: {state['option_contracts']}")
                print(f"   Entry: R${state['entry_price']:.2f}")
                print(f"   Current Bid: R${current_bid:.2f}")
                print(f"   P&L: R${pnl:.2f} ({pnl_percent:.1f}%)")
                
                # Exit logic
                should_exit = False
                exit_reason = ""
                
                # Take profit at 50%
                if pnl_percent > 50:
                    should_exit = True
                    exit_reason = "Take profit (50%+)"
                
                # Stop loss at -50%
                elif pnl_percent < -50:
                    should_exit = True
                    exit_reason = "Stop loss (-50%)"
                  # Check expiry
                expiry_check = check_option_expiry(holding_option)
                if expiry_check['should_close']:
                    should_exit = True
                    exit_reason = f"Near expiry ({expiry_check['days_to_expiry']} days)"
                
                if should_exit:
                    print(f"💰 Exit signal: {exit_reason}")
                    
                    # Execute sell order via CedroTech API
                    print(f"📤 Executing OPTIONS SELL order via CedroTech API...")
                    order_result = api.place_sell_order(
                        ticker=holding_option,
                        quantity=state['option_contracts'],
                        order_type="MARKET"
                    )
                    
                    if order_result.get('success'):
                        print(f"✅ Options sell order executed: {order_result.get('order_id')}")
                        
                        # Send email notification
                        send_email(
                            "OPTIONS TRADE - SELL", 
                            f"Sold {state['option_contracts']} contracts of {holding_option} at R${current_bid:.2f}\n"
                            f"Entry price: R${state['entry_price']:.2f}\n"
                            f"Exit reason: {exit_reason}\n"
                            f"P&L: R${pnl:.2f} ({pnl_percent:.1f}%)"
                        )
                        
                        # Update balance after successful sell order
                        balance_manager.update_balance_after_trade(
                            trade_type='sell',
                            ticker=holding_option,
                            price=current_bid,
                            volume=state['option_contracts']
                        )
                        
                        # Update state
                        state['holding_option'] = None
                        state['option_contracts'] = 0
                        state['entry_price'] = None
                        state['daily_trades_count'] += 1
                        state['daily_pnl'] += pnl
                        
                        # Update balance in state
                        current_balance_info = balance_manager.get_current_balance()
                        state['account_balance'] = current_balance_info['balance']
                        
                        save_options_state(state)
                        
                        print(f"✅ Options trade completed. P&L: R${pnl:.2f}")
                        print(f"💰 Updated Balance: R${current_balance_info['balance']:.2f}")
                    else:
                        print(f"❌ Options sell order failed: {order_result.get('error')}")
                
            else:
                print(f"⚠️ Option no longer tradeable: {validation['reason']}")
                # Force exit if option becomes illiquid
                # TODO: Implement emergency exit logic
        
        print(f"\n⏰ Next check in 2 minutes...")
        time.sleep(120)  # Check every 2 minutes (options move fast)

def is_market_hours():
    """Check if current time is within market hours"""
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    
    # Check if it's a weekday (Monday=0, Sunday=6)
    weekday = now.weekday()
    if weekday >= 5:  # Saturday or Sunday
        return False
    
    # Convert to comparable time format
    market_open = datetime.strptime(MARKET_OPEN_TIME, "%H:%M").time()
    market_close = datetime.strptime(MARKET_CLOSE_TIME, "%H:%M").time()
    current_time_obj = datetime.strptime(current_time, "%H:%M").time()
    
    return market_open <= current_time_obj <= market_close

def should_force_close_positions():
    """Check if we should force close all positions (near market close)"""
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    force_close = datetime.strptime(FORCE_CLOSE_TIME, "%H:%M").time()
    current_time_obj = datetime.strptime(current_time, "%H:%M").time()
    
    return current_time_obj >= force_close

if __name__ == "__main__":
    print("🎯 OPTIONS TRADING ROBOT")
    print("=" * 50)
    print("Choose trading environment:")
    print("1. Paper Trading (Simulation)")
    print("2. Live Trading (Real Money)")
    print("=" * 50)
    
    env_mode = input("Select environment (1 or 2): ").strip()
    paper_trading = env_mode != '2'
    
    if paper_trading:
        print("🟢 PAPER TRADING MODE - Simulated orders only")
    else:
        print("🔴 LIVE TRADING MODE - Real money at risk!")
        confirm = input("Are you sure? This will use real money for OPTIONS! (y/n): ").strip().lower()
        if confirm != 'y':
            print("Switching to paper trading mode for safety.")
            paper_trading = True
    
    try:
        # Get current balance from balance manager
        from utils.balance_manager import BalanceManager
        balance_manager = BalanceManager()
        balance_info = balance_manager.get_current_balance()
        account_balance = balance_info['balance']
        
        print(f"\n💰 Current Balance: R${account_balance:.2f} (Source: {balance_info['source']})")
        print(f"🎯 Max Risk Per Trade: {MAX_RISK_PER_TRADE*100}% = R${account_balance * MAX_RISK_PER_TRADE:.2f}")
        print(f"📊 Daily Trade Limit: {MAX_DAILY_OPTIONS_TRADES} trades")
        
        print("\nStarting options trading robot...")
        monitor_and_trade_options(account_balance, paper_trading=paper_trading)
        
    except KeyboardInterrupt:
        print("\n🛑 Options robot stopped by user")
    except Exception as e:
        print(f"\n❌ Options robot error: {e}")
        import traceback
        traceback.print_exc()
