import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import os
from dotenv import load_dotenv
from utils.strategy import calculate_moving_averages, calculate_rsi, calculate_macd, generate_signals
from utils.database import fetch_daily_analysis, fetch_asset_analysis, fetch_historical_prices
from utils.technical_analysis import run_technical_analysis, calculate_stop_loss_take_profit_levels, calculate_position_size, apply_stop_loss_take_profit
from utils.cedrotech_api_correct import CedroTechAPICorrect
from utils.balance_manager import BalanceManager
import json
from datetime import datetime, timedelta

load_dotenv()

STATE_FILE = 'robot_state.json'

# DAY TRADING CONFIGURATION
MARKET_OPEN_TIME = "09:00"  # 9:00 AM Brazil time
MARKET_CLOSE_TIME = "17:30"  # 5:30 PM Brazil time
FORCE_CLOSE_TIME = "17:00"  # Force close 30 minutes before market close
MAX_DAILY_TRADES = 3  # Maximum trades per day (day trading limit)
DAILY_LOSS_LIMIT = 0.05  # Stop trading if daily loss exceeds 5%

def initialize_trading_api(paper_trading=True):
    """Initialize CedroTech API for live trading"""
    try:
        api = CedroTechAPICorrect(paper_trading=paper_trading)
        print(f"✅ CedroTech API initialized successfully")
        print(f"   Mode: {'PAPER TRADING' if paper_trading else 'LIVE TRADING'}")
        return api
    except Exception as e:
        print(f"❌ Failed to initialize CedroTech API: {e}")
        return None

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
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            print(f"Email sent: {subject}")
    except Exception as e:
        print(f"Failed to send email: {e}")

# fetch_realtime_data() function removed - unused and redundant with database functions

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                state = json.load(f)
                
                # Check if we need to reset for a new trading day
                if should_reset_for_new_day(state):
                    print("🔄 New trading day detected - resetting state for fresh analysis...")
                    state = reset_state()
                    save_state(state)
                
                return state
        except Exception as e:
            print(f"Failed to load state: {e}")
    return {
        'holding_asset': None,
        'position_size': 0,
        'buy_price': None,
        'stop_loss': None,
        'take_profit': None,
        'last_analysis_date': None
    }

def should_reset_for_new_day(state):
    """Check if we should reset state for a new trading day"""
    last_analysis = state.get('last_analysis_date')
    if not last_analysis:
        return True
    
    try:
        last_date = datetime.strptime(last_analysis, '%Y-%m-%d')
        today = datetime.now()
        
        # Reset if it's a new day and we're before market close (typically 6 PM Brazil time)
        if last_date.date() < today.date():
            return True
            
        # Also reset if more than 18 hours have passed (in case market closed)
        hours_diff = (today - last_date).total_seconds() / 3600
        if hours_diff > 18:
            return True
            
    except (ValueError, TypeError):
        return True
    
    return False

def reset_state():
    """Reset the trading state for a new day"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Initialize balance manager to get current balance
    balance_manager = BalanceManager()
    balance_info = balance_manager.get_current_balance()
    current_balance = balance_info['balance']
    
    return {
        'holding_asset': None,
        'position_size': 0,
        'buy_price': None,
        'stop_loss': None,
        'take_profit': None,
        'last_analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'trading_date': today,
        'daily_trades_count': 0,
        'daily_initial_balance': current_balance,
        'account_balance': current_balance
    }

# force_reset_analysis() function removed - unused, functionality available via reset_robot_state.py

def update_analysis_timestamp(state):
    """Update the last analysis timestamp"""
    state['last_analysis_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return state

def save_state(state):
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f)
    except Exception as e:
        print(f"Failed to save state: {e}")

def backtest_strategy(ticker=None, start_date=None, end_date=None, initial_balance=500, risk_per_trade=0.02):
    """
    Backtest the trading strategy for a specific ticker or all tickers.
    
    Args:
        ticker (str): Specific ticker to backtest, or None for all tickers
        start_date (str): Start date for backtesting (YYYY-MM-DD format)
        end_date (str): End date for backtesting (YYYY-MM-DD format)
        initial_balance (float): Starting account balance
        risk_per_trade (float): Risk percentage per trade (0.02 = 2%)
    
    Returns:
        dict: Backtesting results with performance metrics
    """
    from utils.backtest_engine import BacktestEngine
    
    print("="*60)
    print("STARTING STRATEGY BACKTEST")
    print("="*60)
    
    # Set default date range if not provided (last 6 months)
    if not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d')
    if not start_date:
        start_date = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
    
    print(f"Backtest Parameters:")
    print(f"  Ticker: {ticker if ticker else 'All tickers'}")
    print(f"  Date Range: {start_date} to {end_date}")
    print(f"  Initial Balance: ${initial_balance:,.2f}")
    print(f"  Risk per Trade: {risk_per_trade*100}%")
    print()
    
    # Create backtest engine
    engine = BacktestEngine(
        initial_balance=initial_balance,
        risk_per_trade=risk_per_trade,
        start_date=start_date,
        end_date=end_date
    )
    
    # Run backtest
    engine.run_backtest(ticker=ticker)
    
    # Get performance metrics
    metrics = engine.calculate_performance_metrics()
    
    # Print summary
    engine.print_summary()
    
    # Save results
    filename = f"backtest_{ticker if ticker else 'all_tickers'}_{start_date}_{end_date}.json"
    engine.save_results(filename)
    
    # Plot results
    chart_filename = f"backtest_{ticker if ticker else 'all_tickers'}_{start_date}_{end_date}_chart.png"
    engine.plot_results(chart_filename)
    
    return {
        'engine': engine,
        'metrics': metrics,
        'trades': engine.trades,
        'equity_curve': engine.equity_curve
    }

def backtesting_loop(tickers_list=None, scenarios=None):
    """
    Run comprehensive backtesting loop across multiple tickers and scenarios.
    
    Args:
        tickers_list (list): List of tickers to test, or None for default list
        scenarios (list): List of scenario configurations, or None for default scenarios
    
    Returns:
        dict: Complete backtesting results for all scenarios and tickers
    """
    from utils.backtest_engine import BacktestEngine
    
    print("="*60)
    print("STARTING COMPREHENSIVE BACKTESTING LOOP")
    print("="*60)
    
    # Default tickers if not provided
    if not tickers_list:
        tickers_list = [
            "PETR4", "VALE3", "ITUB4", "AMER3", "B3SA3", "MGLU3", "LREN3", 
            "ITSA4", "BBAS3", "RENT3", "ABEV3", "SUZB3", "WEG3", "BRFS3", 
            "BBDC4", "CRFB3", "BPAC11", "GGBR3", "EMBR3", "CMIN3"
        ]
    
    # Default scenarios if not provided
    if not scenarios:
        scenarios = [
            {"initial_balance": 500, "risk_per_trade": 0.01, "name": "Conservative"},
            {"initial_balance": 500, "risk_per_trade": 0.20, "name": "Moderate"},
            {"initial_balance": 500, "risk_per_trade": 0.50, "name": "Aggressive"}
        ]
    
    # Date range for testing (last 6 months)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    
    all_results = {}
    summary_results = {}
    
    print(f"Testing {len(scenarios)} scenarios across {len(tickers_list)} tickers")
    print(f"Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print()
    
    for scenario in scenarios:
        print(f"\n{'='*50}")
        print(f"TESTING {scenario['name'].upper()} SCENARIO")
        print(f"{'='*50}")
        print(f"Risk per trade: {scenario['risk_per_trade']*100}%")
        print(f"Initial balance: ${scenario['initial_balance']:,.2f}")
        
        scenario_results = {}
        
        # Create backtest engine for this scenario
        engine = BacktestEngine(
            initial_balance=scenario['initial_balance'],
            risk_per_trade=scenario['risk_per_trade'],
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d')
        )
        
        # Test each ticker
        for ticker in tickers_list:
            try:
                print(f"\n--- Testing {ticker} ---")
                
                # Reset engine for new ticker
                engine.current_balance = engine.initial_balance
                engine.position = None
                engine.position_size = 0
                engine.entry_price = 0
                engine.trades = []
                engine.equity_curve = []
                
                # Run backtest for this ticker
                engine.backtest_single_ticker(ticker)
                
                # Get metrics for this ticker
                ticker_metrics = engine.calculate_performance_metrics()
                scenario_results[ticker] = ticker_metrics
                
                print(f"Results for {ticker}:")
                print(f"  Total Return: {ticker_metrics.get('total_return', 0):.2f}%")
                print(f"  Win Rate: {ticker_metrics.get('win_rate', 0):.2f}%")
                print(f"  Max Drawdown: {ticker_metrics.get('max_drawdown', 0):.2f}%")
                
            except Exception as e:
                print(f"Error testing {ticker}: {e}")
                scenario_results[ticker] = {"error": str(e)}
        
        all_results[scenario['name']] = scenario_results
        
        # Calculate scenario summary
        valid_results = [r for r in scenario_results.values() if 'error' not in r and r.get('total_return') is not None]
        if valid_results:
            avg_return = sum(r.get('total_return', 0) for r in valid_results) / len(valid_results)
            avg_win_rate = sum(r.get('win_rate', 0) for r in valid_results) / len(valid_results)
            avg_drawdown = sum(r.get('max_drawdown', 0) for r in valid_results) / len(valid_results)
            avg_sharpe = sum(r.get('sharpe_ratio', 0) for r in valid_results) / len(valid_results)
            
            summary_results[scenario['name']] = {
                'avg_return': avg_return,
                'avg_win_rate': avg_win_rate,
                'avg_max_drawdown': avg_drawdown,
                'avg_sharpe_ratio': avg_sharpe,
                'successful_tests': len(valid_results),
                'total_tests': len(tickers_list)
            }
        
        # Save scenario results
        scenario_filename = f"backtesting_loop_{scenario['name'].lower()}_results.json"
        with open(scenario_filename, 'w') as f:
            json.dump(scenario_results, f, indent=2, default=str)
        
        print(f"\nScenario results saved to: {scenario_filename}")
    
    # Print final comparison
    print("\n" + "="*80)
    print("FINAL SCENARIO COMPARISON")
    print("="*80)
    print(f"{'Scenario':<15} {'Avg Return %':<12} {'Avg Win Rate %':<15} {'Avg Max DD %':<12} {'Avg Sharpe':<10}")
    print("-"*80)
    
    for name, summary in summary_results.items():
        print(f"{name:<15} {summary.get('avg_return', 0):<12.2f} "
              f"{summary.get('avg_win_rate', 0):<15.2f} {summary.get('avg_max_drawdown', 0):<12.2f} "
              f"{summary.get('avg_sharpe_ratio', 0):<10.2f}")
    
    # Save complete results
    complete_results = {
        'scenarios': all_results,
        'summary': summary_results,
        'parameters': {
            'tickers_tested': tickers_list,
            'scenarios_tested': scenarios,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d')
        }
    }
    
    with open('complete_backtesting_loop_results.json', 'w') as f:
        json.dump(complete_results, f, indent=2, default=str)
    
    print(f"\nComplete results saved to: complete_backtesting_loop_results.json")
    
    return complete_results

def monitor_and_trade(account_balance, risk_per_trade, paper_trading=True):
    """Enhanced day trading monitor with end-of-day closure and daily limits."""
    from utils.database import fetch_intraday_prices, insert_trade_asset
    from utils.quick_technical_analysis import get_price_signals, fetch_and_store_intraday_for_all
    
    # Initialize CedroTech API
    api = initialize_trading_api(paper_trading=paper_trading)
    if not api:
        print("❌ Cannot start trading without API connection")
        return
    
    # Initialize Balance Manager for dynamic balance tracking
    balance_manager = BalanceManager(api=api)
    
    state = load_state()
    
    # Initialize daily tracking if new day
    today = datetime.now().strftime('%Y-%m-%d')
    if state.get('trading_date') != today:
        # Get current balance for new trading day
        balance_info = balance_manager.get_current_balance()
        current_balance = balance_info['balance']
        
        state['trading_date'] = today
        state['daily_trades_count'] = 0
        state['daily_initial_balance'] = current_balance
        state['account_balance'] = current_balance
        save_state(state)
        print(f"🌅 New trading day started: {today}")
        print(f"💰 Starting balance: R${current_balance:.2f} (Source: {balance_info['source']})")
    
    tickers = [
        "PETR4", "VALE3", "ITUB4", "AMER3", "B3SA3", "MGLU3", "LREN3", "ITSA4", "BBAS3", "RENT3", "ABEV3", "SUZB3", "WEG3", "BRFS3", "BBDC4", "CRFB3", "BPAC11", "GGBR3", "EMBR3", "CMIN3", "ITSA4", "RDOR3", "RAIZ4", "PETZ3", "PSSA3", "VBBR3"]
    
    print("🤖 Starting Day Trading Robot - Enhanced Mode")
    print(f"📊 Daily Limits: Max {MAX_DAILY_TRADES} trades, Max {DAILY_LOSS_LIMIT*100}% loss")
    print(f"🔗 Trading API: {'PAPER MODE' if paper_trading else 'LIVE MODE'}")
    
    while True:
        current_time = datetime.now().strftime("%H:%M")
          # 🚨 CRITICAL: Check if market is closed
        if not is_market_hours():
            print(f"🕐 Market closed ({current_time}). Day trading robot stopped.")
            # Force close any remaining positions
            force_close_all_positions(state, account_balance, api, balance_manager)
            break
        
        # 🚨 CRITICAL: Force close positions near market close
        if should_force_close_positions():
            if force_close_all_positions(state, account_balance, api, balance_manager):
                print("✅ All positions closed for day trading compliance.")
            continue
          # Check daily limits
        if get_daily_trades_count(state) >= MAX_DAILY_TRADES:
            print(f"📈 Daily trade limit reached ({MAX_DAILY_TRADES}). No more trades today.")
            time.sleep(300)
            continue
            
        if is_daily_loss_limit_reached(state):
            print(f"🛑 Daily loss limit reached ({DAILY_LOSS_LIMIT*100}%). Stopping trading.")
            force_close_all_positions(state, account_balance, api, balance_manager)
            break
        
        holding_asset = state.get('holding_asset')
        position_size = state.get('position_size', 0)
        buy_price = state.get('buy_price')
        stop_loss = state.get('stop_loss')
        take_profit = state.get('take_profit')

        if holding_asset is None:
            print("🔍 Scanning for day trading opportunities...")
            run_technical_analysis()
            print("📡 Fetching latest intraday data...")
            fetch_and_store_intraday_for_all(tickers, interval='1d', range_='1mo')
            
            print("🎯 Selecting best day trading asset...")
            best_asset = None
            best_score = float('-inf')
            
            for ticker in tickers:
                print(f"📊 Analyzing {ticker}...")
                daily_analysis = fetch_daily_analysis(ticker)
                asset_analysis = fetch_asset_analysis(ticker)
                historical_prices = fetch_historical_prices(ticker)
                
                if not daily_analysis or not asset_analysis or not historical_prices:
                    print(f"⚠️ Insufficient data for {ticker}. Skipping...")
                    continue
                
                rsi = next((row.get('rsi') for row in daily_analysis if row.get('rsi') is not None), None)
                beta_raw = asset_analysis[0].get('beta')
                
                try:
                    beta = float(beta_raw) if beta_raw is not None else None
                except (TypeError, ValueError):
                    print(f"⚠️ Invalid beta for {ticker}. Attempting calculation...")
                    from utils.technical_analysis import calculate_beta_from_returns
                    beta = calculate_beta_from_returns(ticker, "IBOV")
                    if beta is None:
                        print(f"❌ Could not calculate beta for {ticker}. Skipping...")
                        continue
                        
                if rsi is None or beta is None:
                    print(f"❌ Missing RSI or beta for {ticker}. Skipping...")
                    continue
                  # Day trading scoring with VOLUME ANALYSIS (prioritize volatility and momentum)
                score = 0
                if 30 <= rsi <= 70:  # Avoid extreme conditions
                    score += 10
                if 0.8 <= beta <= 1.5:  # Moderate volatility
                    score += 15
                if rsi < 40:  # Oversold potential
                    score += 5
                if beta > 1.0:  # Higher volatility for day trading
                    score += 10
                
                # ENHANCED: Add volume analysis for better day trading selection
                if historical_prices and len(historical_prices) >= 20:
                    from utils.technical_analysis import analyze_volume_profile
                    
                    # Extract price and volume data for analysis
                    recent_prices = [p['close'] for p in historical_prices[-20:]]
                    recent_volumes = [p['volume'] for p in historical_prices[-20:] if p.get('volume')]
                    
                    if recent_volumes and len(recent_volumes) >= 15:
                        current_price = recent_prices[-1]
                        volume_analysis = analyze_volume_profile(recent_prices, recent_volumes, current_price)
                        
                        # Volume-based scoring boost for day trading
                        liquidity_score = volume_analysis.get("liquidity_score", 0)
                        volume_trend = volume_analysis.get("volume_trend", "neutral")
                        breakout_potential = volume_analysis.get("breakout_potential", False)
                        volume_surge = volume_analysis.get("volume_surge", False)
                        
                        # Apply volume scoring
                        if liquidity_score > 70:  # High liquidity - excellent for day trading
                            score += 20
                        elif liquidity_score > 50:  # Good liquidity
                            score += 10
                        elif liquidity_score < 30:  # Poor liquidity - risky for day trading
                            score -= 15
                        
                        if volume_trend == "up":  # Volume supporting price action
                            score += 10
                        
                        if breakout_potential:  # High breakout potential
                            score += 15
                        
                        if volume_surge and rsi < 50:  # Volume surge with reasonable RSI
                            score += 12
                        
                        print(f"📊 Volume Analysis - {ticker}: Liquidity: {liquidity_score}, Trend: {volume_trend}, Breakout: {breakout_potential}")
                    else:
                        print(f"⚠️ Limited volume data for {ticker} - using basic scoring")
                    
                    # Extract price and volume data for analysis
                    recent_prices = [p['close'] for p in historical_prices[-20:]]
                    recent_volumes = [p['volume'] for p in historical_prices[-20:] if p.get('volume')]
                    
                    if recent_volumes and len(recent_volumes) >= 15:
                        current_price = recent_prices[-1]
                        volume_analysis = analyze_volume_profile(recent_prices, recent_volumes, current_price)
                        
                        # Volume-based scoring boost for day trading
                        liquidity_score = volume_analysis.get("liquidity_score", 0)
                        volume_trend = volume_analysis.get("volume_trend", "neutral")
                        breakout_potential = volume_analysis.get("breakout_potential", False)
                        volume_surge = volume_analysis.get("volume_surge", False)
                        
                        # Apply volume scoring
                        if liquidity_score > 70:  # High liquidity - excellent for day trading
                            score += 20
                        elif liquidity_score > 50:  # Good liquidity
                            score += 10
                        elif liquidity_score < 30:  # Poor liquidity - risky for day trading
                            score -= 15
                        
                        if volume_trend == "up":  # Volume supporting price action
                            score += 10
                        
                        if breakout_potential:  # High breakout potential
                            score += 15
                        
                        if volume_surge and rsi < 50:  # Volume surge with reasonable RSI
                            score += 12
                        
                        print(f"📊 Volume Analysis - {ticker}: Liquidity: {liquidity_score}, Trend: {volume_trend}, Breakout: {breakout_potential}")
                    else:
                        print(f"⚠️ Limited volume data for {ticker} - using basic scoring")
                        
                print(f"📈 Score for {ticker}: {score} (RSI: {rsi:.1f}, Beta: {beta:.2f})")
                
                if score > best_score:
                    best_score = score
                    best_asset = ticker
                    
            if not best_asset:
                print("❌ No suitable day trading asset found.")
                print("⏳ Waiting 5 minutes before next scan...")
                time.sleep(300)
                continue
                
            print(f"🎯 Selected for day trading: {best_asset} (Score: {best_score})")
            historical_prices = fetch_historical_prices(best_asset)
            stop_loss, take_profit = calculate_stop_loss_take_profit_levels(historical_prices)
            
            state['holding_asset'] = best_asset
            state['buy_price'] = None
            state['position_size'] = 0
            state['stop_loss'] = stop_loss
            state['take_profit'] = take_profit
              # Update analysis timestamp
            state = update_analysis_timestamp(state)
            save_state(state)
            
        else:
            print(f"👀 Monitoring {holding_asset} for day trading signals...")
            intraday_prices = fetch_intraday_prices(holding_asset)
            signal, high, low = get_price_signals(intraday_prices)
            print(f"📊 Signal: {signal}, High: {high}, Low: {low}")
            
            current_price = intraday_prices[0]['close'] if intraday_prices else None
            if buy_price is None and signal == 'buy' and current_price:
                print("🚀 BUY signal detected. Executing day trade...")
                
                # Use BalanceManager for dynamic position sizing
                stop_loss_distance = abs(current_price - stop_loss)
                position_result = balance_manager.calculate_position_size_with_current_balance(
                    risk_per_trade, stop_loss_distance
                )
                
                if not position_result['success']:
                    print(f"❌ Position sizing failed: {position_result['error']}")
                    continue
                
                position_size = position_result['position_size']
                
                # Validate trade affordability
                affordability_check = balance_manager.validate_trade_affordability(
                    holding_asset, position_size, current_price
                )
                if not affordability_check['affordable']:
                    print(f"❌ Insufficient balance for trade: {affordability_check['message']}")
                    continue
                
                # Execute API buy order
                print(f"📤 Executing BUY order via CedroTech API...")
                order_result = api.place_buy_order(
                    ticker=holding_asset,
                    quantity=int(position_size),
                    order_type="MARKET"
                )
                
                if order_result.get('success'):
                    print(f"✅ Buy order executed: {order_result.get('order_id')}")
                    
                    # Update balance after successful buy order
                    balance_manager.update_balance_after_trade(
                        trade_type='buy',
                        ticker=holding_asset,
                        price=current_price,
                        volume=position_size
                    )
                    
                    state['buy_price'] = current_price
                    state['position_size'] = position_size
                    state['daily_trades_count'] = get_daily_trades_count(state) + 1
                    
                    # Update state with current balance
                    current_balance_info = balance_manager.get_current_balance()
                    state['account_balance'] = current_balance_info['balance']
                    
                    send_email("DAY TRADE - BUY", f"Bought {position_size} of {holding_asset} at {current_price}")
                    insert_trade_asset((holding_asset, 'buy', current_price, position_size))
                    save_state(state)
                else:
                    print(f"❌ Buy order failed: {order_result.get('error')}")
                
            elif buy_price is not None and (signal == 'sell' or apply_stop_loss_take_profit(current_price, stop_loss, take_profit) == 'stop_loss'):
                print("💰 SELL signal or stop-loss detected. Closing day trade...")
                  # Execute API sell order
                print(f"📤 Executing SELL order via CedroTech API...")
                order_result = api.place_sell_order(
                    ticker=holding_asset,
                    quantity=int(position_size),
                    order_type="MARKET"
                )
                
                if order_result.get('success'):
                    print(f"✅ Sell order executed: {order_result.get('order_id')}")
                    
                    # Update balance after successful sell order
                    balance_manager.update_balance_after_trade(
                        trade_type='sell',
                        ticker=holding_asset,
                        price=current_price,
                        volume=position_size
                    )
                    
                    # Calculate P&L
                    pnl = (current_price - buy_price) * position_size
                    pnl_percent = ((current_price - buy_price) / buy_price) * 100
                    
                    send_email("DAY TRADE - SELL", f"Sold {holding_asset} at {current_price} (P&L: {pnl:.2f} R$ / {pnl_percent:.2f}%)")
                    insert_trade_asset((holding_asset, 'sell', current_price, position_size))
                    
                    # Update state with current balance from BalanceManager
                    current_balance_info = balance_manager.get_current_balance()
                    state['account_balance'] = current_balance_info['balance']
                    
                    # Clear position
                    state['holding_asset'] = None
                    state['buy_price'] = None
                    state['position_size'] = 0
                    state['stop_loss'] = None
                    state['take_profit'] = None
                    save_state(state)
                    
                    print(f"✅ Day trade completed. P&L: {pnl:.2f} R$ ({pnl_percent:.2f}%)")
                    print(f"💰 Updated Balance: R${current_balance_info['balance']:.2f}")
                else:
                    print(f"❌ Sell order failed: {order_result.get('error')}")
                    
            else:
                print("⏸️ No action taken. Monitoring continues...")
                
            time.sleep(300)  # 5-minute intervals for day trading
            
        # Always save state at the end of each loop
        save_state(state)
    

def balance_and_risk_management():
    """Get current account balance and apply dynamic risk management."""
    balance_manager = BalanceManager()
    balance_info = balance_manager.get_current_balance()
    account_balance = balance_info['balance']
    risk_per_trade = 0.02  # Risk 2% of current account balance per trade
    
    print(f"💰 Current Account Balance: R${account_balance:.2f} (Source: {balance_info['source']})")
    print(f"⚠️ Risk per Trade: {risk_per_trade*100}% = R${account_balance * risk_per_trade:.2f}")
    
    return account_balance, risk_per_trade

def run_backtesting_menu():
    """Interactive menu for running backtesting functions."""
    print("\n" + "="*60)
    print("TRADING ROBOT - BACKTESTING MENU")
    print("="*60)
    print("1. Single Strategy Backtest (backtest_strategy)")
    print("2. Comprehensive Backtesting Loop (backtesting_loop)")
    print("3. Quick Single Ticker Test")
    print("4. Custom Scenario Test")
    print("5. Return to Live Trading")
    print("="*60)
    
    choice = input("Select an option (1-5): ").strip()
    
    if choice == '1':
        # Single strategy backtest
        ticker = input("Enter ticker (or press Enter for all tickers): ").strip().upper()
        ticker = ticker if ticker else None
        
        start_date = input("Enter start date (YYYY-MM-DD) or press Enter for default: ").strip()
        start_date = start_date if start_date else None
        
        end_date = input("Enter end date (YYYY-MM-DD) or press Enter for default: ").strip()
        end_date = end_date if end_date else None
        balance = input("Enter initial balance (or press Enter for $500): ").strip()
        balance = int(float(balance)) if balance else 500
        
        risk = input("Enter risk per trade (0.01-0.1) or press Enter for 0.02: ").strip()
        risk = float(risk) if risk else 0.02
        
        print("\nStarting single strategy backtest...")
        results = backtest_strategy(ticker, start_date, end_date, balance, risk)
        print(f"\nBacktest completed! Results saved and charts generated.")
        
    elif choice == '2':
        # Comprehensive backtesting loop
        print("Running comprehensive backtesting loop with default settings...")
        print("This will test Conservative, Moderate, and Aggressive scenarios.")
        
        confirm = input("Continue? (y/n): ").strip().lower()
        if confirm == 'y':
            results = backtesting_loop()
            print(f"\nComprehensive backtesting completed! Check generated files for detailed results.")
        
    elif choice == '3':
        # Quick single ticker test
        print("\nAvailable tickers: PETR4, VALE3, ITUB4, AMER3, B3SA3, MGLU3, LREN3")
        ticker = input("Enter ticker for quick test: ").strip().upper()
        
        if ticker:
            print(f"\nRunning quick backtest for {ticker}...")
            results = backtest_strategy(ticker, initial_balance=500, risk_per_trade=0.02)
            print(f"\nQuick test completed for {ticker}!")
        
    elif choice == '4':
        # Custom scenario test
        print("\nCustom Scenario Configuration:")
        
        tickers = input("Enter tickers separated by commas (or press Enter for default): ").strip().upper()
        if tickers:
            tickers_list = [t.strip() for t in tickers.split(',')]
        else:
            tickers_list = None
            
        balance = input("Enter initial balance (default 500): ").strip()
        balance = float(balance) if balance else 500
        
        risk_low = input("Enter conservative risk (default 0.01): ").strip()
        risk_low = float(risk_low) if risk_low else 0.01
        
        risk_high = input("Enter aggressive risk (default 0.05): ").strip()
        risk_high = float(risk_high) if risk_high else 0.50
        
        scenarios = [
            {"initial_balance": balance, "risk_per_trade": risk_low, "name": "Custom_Conservative"},
            {"initial_balance": balance, "risk_per_trade": (risk_low + risk_high) / 2, "name": "Custom_Moderate"},
            {"initial_balance": balance, "risk_per_trade": risk_high, "name": "Custom_Aggressive"}
        ]
        
        print("\nRunning custom backtesting scenarios...")
        results = backtesting_loop(tickers_list, scenarios)
        print(f"\nCustom backtesting completed!")
        
    elif choice == '5':
        print("Returning to live trading mode...")
        return False
    
    else:
        print("Invalid choice. Please try again.")
    
    return True

def is_market_hours():
    """Check if current time is within market hours"""
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    
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

def get_daily_trades_count(state):
    """Get number of trades executed today"""
    return state.get('daily_trades_count', 0)

def calculate_daily_pnl(state):
    """Calculate today's profit/loss percentage"""
    initial_balance = state.get('daily_initial_balance', state.get('account_balance', 500))
    current_balance = state.get('account_balance', initial_balance)
    return (current_balance - initial_balance) / initial_balance

def is_daily_loss_limit_reached(state):
    """Check if daily loss limit has been reached"""
    daily_pnl = calculate_daily_pnl(state)
    return daily_pnl <= -DAILY_LOSS_LIMIT

def force_close_all_positions(state, account_balance, api=None, balance_manager=None):
    """Force close all open positions at market close"""
    from utils.database import fetch_intraday_prices, insert_trade_asset
    
    holding_asset = state.get('holding_asset')
    position_size = state.get('position_size', 0)
    buy_price = state.get('buy_price')
    
    if holding_asset and position_size > 0 and buy_price:
        print("🚨 FORCE CLOSING POSITION - MARKET CLOSE APPROACHING 🚨")
        
        # Get current price
        intraday_prices = fetch_intraday_prices(holding_asset)
        current_price = intraday_prices[0]['close'] if intraday_prices else buy_price
        
        # Execute API sell order if available
        if api:
            print(f"📤 Executing FORCE SELL order via CedroTech API...")
            order_result = api.place_sell_order(
                ticker=holding_asset,
                quantity=int(position_size),
                order_type="MARKET"
            )
            
            if order_result.get('success'):
                print(f"✅ Force sell order executed: {order_result.get('order_id')}")
            else:
                print(f"❌ Force sell order failed: {order_result.get('error')}")
        
        # Update balance after successful force sell order
        if balance_manager:
            balance_manager.update_balance_after_trade(
                trade_type='force_close',
                ticker=holding_asset,
                price=current_price,
                volume=position_size
            )
        
        # Calculate P&L
        pnl = (current_price - buy_price) * position_size
        pnl_percent = ((current_price - buy_price) / buy_price) * 100
        
        # Execute force sell
        send_email("DAY TRADING - FORCE CLOSE", 
                  f"Force closed {position_size} shares of {holding_asset} at {current_price} "
                  f"(P&L: {pnl:.2f} R$ / {pnl_percent:.2f}%)")
        
        # Log trade
        insert_trade_asset((holding_asset, 'force_close', current_price, position_size))
        
        # Update state with current balance from BalanceManager
        if balance_manager:
            current_balance_info = balance_manager.get_current_balance()
            state['account_balance'] = current_balance_info['balance']
            print(f"💰 Updated Balance: R${current_balance_info['balance']:.2f}")
        else:
            # Fallback to manual calculation if no balance manager
            state['account_balance'] = state.get('account_balance', account_balance) + pnl
        
        # Clear position
        state['holding_asset'] = None
        state['buy_price'] = None
        state['position_size'] = 0
        state['stop_loss'] = None
        state['take_profit'] = None
        
        print(f"✅ Position closed. P&L: {pnl:.2f} R$ ({pnl_percent:.2f}%)")
        
        save_state(state)
        return True
    
    return False

if __name__ == "__main__":
    print("="*60)
    print("AUTOMATED TRADING ROBOT")
    print("="*60)
    print("Choose mode:")
    print("1. Live Trading")
    print("2. Backtesting")
    print("="*60)
    
    mode = input("Select mode (1 or 2): ").strip()
    
    if mode == '2':
        # Backtesting mode
        while run_backtesting_menu():
            continue
    else:
        # Live trading mode (default)
        print("\nLive Trading Mode Selected")
        print("="*40)
        print("Choose trading environment:")
        print("1. Paper Trading (Simulation)")
        print("2. Live Trading (Real Money)")
        print("="*40)
        
        env_mode = input("Select environment (1 or 2): ").strip()
        paper_trading = env_mode != '2'
        
        if paper_trading:
            print("🟢 PAPER TRADING MODE - Simulated orders only")
        else:
            print("🔴 LIVE TRADING MODE - Real money at risk!")
            confirm = input("Are you sure? This will use real money! (y/n): ").strip().lower()
            if confirm != 'y':
                print("Switching to paper trading mode for safety.")
                paper_trading = True
        
        print("\nStarting trading robot...")
        account_balance, risk_per_trade = balance_and_risk_management()
        monitor_and_trade(account_balance, risk_per_trade, paper_trading)