import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import os
from dotenv import load_dotenv
from utils.strategy import calculate_moving_averages, calculate_rsi, calculate_macd, generate_signals
from utils.database import fetch_daily_analysis, fetch_asset_analysis, fetch_historical_prices
from utils.technical_analysis import run_technical_analysis, calculate_stop_loss_take_profit_levels, calculate_position_size, apply_stop_loss_take_profit
import json
from datetime import datetime, timedelta

load_dotenv()

STATE_FILE = 'robot_state.json'

def send_email(subject, body):
    """Send an email notification."""
    sender_email = os.environ.get('GMAIL')  
    sender_password = os.environ.get('PASS')
    receiver_email = os.environ.get('GMAIL') 

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

def fetch_realtime_data(ticker):
    """Fetch the most recent price and related info for a given ticker from the database (as a real-time proxy)."""
    prices = fetch_historical_prices(ticker)
    if not prices:
        print(f"No historical price data found for {ticker}.")
        return None
    latest = prices[0]  # Most recent due to order(desc=True) in fetch_historical_prices
    # Map to expected keys for trading logic
    return {
        'symbol': latest.get('ticker'),
        'regularMarketPrice': latest.get('close'),
        'regularMarketDayHigh': latest.get('high'),
        'regularMarketDayLow': latest.get('low'),
        'regularMarketOpen': latest.get('open'),
        'regularMarketVolume': latest.get('volume'),
        'date': latest.get('date'),
        # Add more fields if needed for your logic
    }

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Failed to load state: {e}")
    return {
        'holding_asset': None,
        'position_size': 0,
        'buy_price': None,
        'stop_loss': None,
        'take_profit': None
    }

def save_state(state):
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f)
    except Exception as e:
        print(f"Failed to save state: {e}")

def backtest_strategy(ticker=None, start_date=None, end_date=None, initial_balance=1000, risk_per_trade=0.02):
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
            {"initial_balance": 1000, "risk_per_trade": 0.01, "name": "Conservative"},
            {"initial_balance": 1000, "risk_per_trade": 0.02, "name": "Moderate"},
            {"initial_balance": 1000, "risk_per_trade": 0.05, "name": "Aggressive"}
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

def monitor_and_trade(account_balance, risk_per_trade):
    """Monitor and analyze the recommended asset, only selecting a new asset when not holding any. State is persisted across restarts and trades are logged to the trade_asset table."""
    from utils.database import fetch_intraday_prices, insert_trade_asset
    from utils.quick_technical_analysis import get_price_signals, fetch_and_store_intraday_for_all
    state = load_state()
    tickers = [
        "PETR4", "VALE3", "ITUB4", "AMER3", "B3SA3", "MGLU3", "LREN3", "ITSA4", "BBAS3", "RENT3", "ABEV3", "SUZB3", "WEG3", "BRFS3", "BBDC4", "CRFB3", "BPAC11", "GGBR3", "EMBR3", "CMIN3", "ITSA4", "RDOR3", "RAIZ4", "PETZ3", "PSSA3", "VBBR3"]
    
    while True:
        holding_asset = state.get('holding_asset')
        position_size = state.get('position_size', 0)
        buy_price = state.get('buy_price')
        stop_loss = state.get('stop_loss')
        take_profit = state.get('take_profit')

        if holding_asset is None:
            print("Running technical analysis to select best asset...")
            run_technical_analysis()
            print("Fetching and storing latest intraday (5m) data for all tickers...")
            fetch_and_store_intraday_for_all(tickers, interval='1d', range_='1mo')
            print("Selecting best asset for trading...")
            best_asset = None
            best_score = float('-inf')
            for ticker in tickers:
                print(f"Analyzing data for {ticker}...")
                daily_analysis = fetch_daily_analysis(ticker)
                asset_analysis = fetch_asset_analysis(ticker)
                historical_prices = fetch_historical_prices(ticker)
                if not daily_analysis or not asset_analysis or not historical_prices:
                    print(f"Insufficient data for {ticker}. Skipping...")
                    continue
                rsi = next((row.get('rsi') for row in daily_analysis if row.get('rsi') is not None), None)
                beta_raw = asset_analysis[0].get('beta')
                try:
                    beta = float(beta_raw)
                except (TypeError, ValueError):
                    print(f"Invalid or missing beta for {ticker} (value: {beta_raw}). Attempting to calculate beta from returns...")
                    from utils.technical_analysis import calculate_beta_from_returns
                    beta = calculate_beta_from_returns(ticker, "IBOV")
                    if beta is None:
                        print(f"Could not calculate beta for {ticker}. Skipping...")
                        continue
                if rsi is None or beta is None:
                    print(f"Missing RSI or beta for {ticker}. Skipping...")
                    continue
                score = 0
                if 30 <= rsi <= 70:
                    score += 10
                if beta < 1:
                    score += 5
                print(f"Score for {ticker}: {score}")
                if score > best_score:
                    best_score = score
                    best_asset = ticker
            if not best_asset:
                print("No suitable asset found for trading today.")
                print("Waiting 5 minutes before next attempt...")
                time.sleep(300)
                continue
            print(f"Best asset for trading: {best_asset}")
            historical_prices = fetch_historical_prices(best_asset)
            stop_loss, take_profit = calculate_stop_loss_take_profit_levels(historical_prices)
            state['holding_asset'] = best_asset
            state['buy_price'] = None
            state['position_size'] = 0
            state['stop_loss'] = stop_loss
            state['take_profit'] = take_profit
            save_state(state)
        else:
            print(f"Monitoring {holding_asset} for trade signals...")
            intraday_prices = fetch_intraday_prices(holding_asset)
            signal, high, low = get_price_signals(intraday_prices)
            print(f"Quick signal: {signal}, High: {high}, Low: {low}")
            current_price = intraday_prices[0]['close'] if intraday_prices else None
            if buy_price is None and signal == 'buy' and current_price:
                print("Buy signal detected. Executing buy...")
                position_size = calculate_position_size(account_balance, risk_per_trade, stop_loss, current_price)
                state['buy_price'] = current_price
                state['position_size'] = position_size
                send_email("Trade Executed", f"Bought {position_size} of {holding_asset} at {current_price}")
                # Log buy trade
                insert_trade_asset((holding_asset, 'buy', current_price, position_size))
                save_state(state)
            elif buy_price is not None and (signal == 'sell' or apply_stop_loss_take_profit(current_price, stop_loss, take_profit) == 'stop_loss'):
                print("Sell signal or stop-loss detected. Executing sell...")
                send_email("Trade Executed", f"Sold {holding_asset} at {current_price}")
                # Log sell trade
                insert_trade_asset((holding_asset, 'sell', current_price, position_size))
                state['holding_asset'] = None
                state['buy_price'] = None
                state['position_size'] = 0
                state['stop_loss'] = None
                state['take_profit'] = None
                save_state(state)
            else:
                print("No action taken. Waiting for next check...")
            time.sleep(300)
        # Always save state at the end of each loop
        save_state(state)
    

def balance_and_risk_management():
    """Check account balance and apply risk management."""
    account_balance = 300  # Example account balance in R$
    risk_per_trade = 0.50  # Risk 2% of account balance per trade

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
        
        balance = input("Enter initial balance (or press Enter for $1000): ").strip()
        balance = float(balance) if balance else 1000
        
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
            results = backtest_strategy(ticker, initial_balance=1000, risk_per_trade=0.02)
            print(f"\nQuick test completed for {ticker}!")
        
    elif choice == '4':
        # Custom scenario test
        print("\nCustom Scenario Configuration:")
        
        tickers = input("Enter tickers separated by commas (or press Enter for default): ").strip().upper()
        if tickers:
            tickers_list = [t.strip() for t in tickers.split(',')]
        else:
            tickers_list = None
            
        balance = input("Enter initial balance (default 1000): ").strip()
        balance = float(balance) if balance else 1000
        
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
        print("Starting live trading mode...")
        account_balance, risk_per_trade = balance_and_risk_management()
        monitor_and_trade(account_balance, risk_per_trade)