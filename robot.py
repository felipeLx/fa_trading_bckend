import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import os
from dotenv import load_dotenv
from utils.strategy import calculate_moving_averages, calculate_rsi, calculate_macd, generate_signals
from utils.database import fetch_daily_analysis, fetch_asset_analysis, fetch_historical_prices
from utils.technical_analysis import run_technical_analysis, calculate_stop_loss_take_profit_levels, calculate_position_size, apply_stop_loss_take_profit

load_dotenv()

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

def monitor_and_trade(account_balance, risk_per_trade):
    """Monitor and analyze the recommended asset."""
    print("Running technical analysis...")
    run_technical_analysis()

    print("Fetching data for analysis...")

    # Fetch data from the database
    tickers = ["PETR4", "VALE3", "ITUB4", "AMER3", "B3SA3", "MGLU3", "LREN3", "ITSA4", "BBAS3", "RENT3", "ABEV3", "SUZB3", "WEG3", "BRFS3", "BBDC4", "CRFB3", "BPAC11", "GGBR3", "EMBR3", "CMIN3", "ITSA4", "RDOR3", "RAIZ4", "PETZ3", "PSSA3", "VBBR3"]
    best_asset = None
    best_score = float('-inf')

    for ticker in tickers:
        print(f"Analyzing data for {ticker}...")

        # Fetch daily analysis and asset analysis data
        daily_analysis = fetch_daily_analysis(ticker)
        asset_analysis = fetch_asset_analysis(ticker)
        historical_prices = fetch_historical_prices(ticker)

        if not daily_analysis or not asset_analysis or not historical_prices:
            print(f"Insufficient data for {ticker}. Skipping...")
            continue

        # Example scoring logic based on RSI and beta
        rsi = next((row.get('rsi') for row in daily_analysis if row.get('rsi') is not None), None)  # Get first non-None RSI
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

        # Favor assets with RSI between 30 and 70 and low beta
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
        return

    print(f"Best asset for trading: {best_asset}")

    # Fetch historical prices for the best asset
    historical_prices = fetch_historical_prices(best_asset)
    stop_loss, take_profit = calculate_stop_loss_take_profit_levels(historical_prices)
    print(f"Stop-loss: {stop_loss}, Take-profit: {take_profit}")

    # --- Use quick technical analysis for real-time trade signals ---
    from utils.database import fetch_intraday_prices
    from utils.quick_technical_analysis import get_price_signals

    while True:
        print(f"Fetching intraday (5m) data for {best_asset}...")
        intraday_prices = fetch_intraday_prices(best_asset)
        signal, high, low = get_price_signals(intraday_prices)
        print(f"Quick signal: {signal}, High: {high}, Low: {low}")

        if signal == 'buy':
            print("Buy signal detected (quick analysis). Calculating position size...")
            current_price = intraday_prices[0]['close'] if intraday_prices else None
            if current_price:
                position_size = calculate_position_size(account_balance, risk_per_trade, stop_loss, current_price)
                #place_order(api_key="your_api_key_here", ticker=best_asset, action="buy", quantity=position_size)
                apply_stop_loss_take_profit(current_price, stop_loss, take_profit)
                send_email("Trade Executed", f"Bought {position_size} of {best_asset} at {current_price}")
        elif signal == 'sell':
            print("Sell signal detected (quick analysis). Executing sell order...")
            current_price = intraday_prices[0]['close'] if intraday_prices else None
            if current_price:
                #place_order(api_key="your_api_key_here", ticker=best_asset, action="sell", quantity=10)  # Example quantity
                send_email("Trade Executed", f"Sold {best_asset} at {current_price}")
        else:
            print("Hold signal (quick analysis). No action taken.")

        print("Waiting for the next check...")
        time.sleep(300)  # Wait 5 minutes before the next check
    

def balance_and_risk_management():
    """Check account balance and apply risk management."""
    account_balance = 300  # Example account balance in R$
    risk_per_trade = 0.50  # Risk 2% of account balance per trade

    return account_balance, risk_per_trade

if __name__ == "__main__":
    account_balance, risk_per_trade = balance_and_risk_management()
    monitor_and_trade(account_balance, risk_per_trade)