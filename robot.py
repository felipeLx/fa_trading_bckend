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
            fetch_and_store_intraday_for_all(tickers, interval='5m', range_='1d')
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

if __name__ == "__main__":
    account_balance, risk_per_trade = balance_and_risk_management()
    monitor_and_trade(account_balance, risk_per_trade)