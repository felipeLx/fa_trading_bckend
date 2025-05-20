import os
import requests
from datetime import datetime, timedelta

def fetch_recent_prices(ticker, interval='5m', range_='1d'):
    """Fetch recent price data for the given ticker from BRAPI."""
    token = os.getenv('BRAPI_API_KEY')
    if not token:
        print("Error: BRAPI_API_KEY is not set in the environment variables.")
        return None
    url = f"https://brapi.dev/api/quote/{ticker}"
    params = {
        'range': range_,
        'interval': interval,
        'token': token,
    }
    try:
        response = requests.get(url, params=params)
        data = response.json()
        if response.status_code == 200 and 'results' in data and data['results']:
            return data['results'][0]['historicalDataPrice']
        else:
            print(f"Failed to fetch data for {ticker}: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None

def get_price_signals(prices):
    """Determine buy/sell/hold signal based on recent high/low."""
    if not prices or len(prices) < 2:
        return None, None, None

    closes = [p['close'] for p in prices if p.get('close') is not None]
    highs = [p['high'] for p in prices if p.get('high') is not None]
    lows = [p['low'] for p in prices if p.get('low') is not None]

    current_price = closes[-1]
    recent_high = max(highs)
    recent_low = min(lows)

    # Simple logic: buy if price breaks above recent high, sell if below recent low
    if current_price >= recent_high:
        signal = 'buy'
    elif current_price <= recent_low:
        signal = 'sell'
    else:
        signal = 'hold'

    return signal, recent_high, recent_low

def fetch_and_store_intraday(ticker, interval='5m', range_='1d'):
    """Fetch recent intraday prices and save them to the database."""
    from utils.database import insert_intraday_prices
    prices = fetch_recent_prices(ticker, interval=interval, range_=range_)
    if prices:
        for candle in prices:
            insert_intraday_prices((
                ticker,
                candle['date'],
                candle['open'],
                candle['high'],
                candle['low'],
                candle['close'],
                candle['volume'],
                candle['adjustedClose']
            ))
    else:
        print(f"No intraday prices to save for {ticker}.")

# Example usage:
if __name__ == "__main__":
    tickers = [
        "PETR4", "VALE3", "ITUB4", "AMER3", "B3SA3", "MGLU3", "LREN3", "ITSA4", "BBAS3", "RENT3", "ABEV3", "SUZB3", "WEG3", "BRFS3", "BBDC4", "CRFB3", "BPAC11", "GGBR3", "EMBR3", "CMIN3", "ITSA4", "RDOR3", "RAIZ4", "PETZ3", "PSSA3", "VBBR3"
    ]
    for ticker in tickers:
        # Fetch from API and store in DB
        fetch_and_store_intraday(ticker, interval='5m', range_='1d')
        # Fetch from DB for analysis and charting
        from utils.database import fetch_intraday_prices
        prices = fetch_intraday_prices(ticker)
        signal, high, low = get_price_signals(prices)
        print(f"{ticker}: Signal: {signal}, High: {high}, Low: {low}")