import pandas as pd
from utils.database import insert_daily_analysis, insert_yearly_analysis, save_balance_sheet_data, save_historical_prices, insert_asset_analysis
import requests
from dotenv import load_dotenv
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib
from utils.asset_analysis import analyze_asset
import numpy as np

load_dotenv()

# ==========================================
# VOLUME ANALYSIS FUNCTIONS FOR DAY TRADING
# ==========================================

def calculate_on_balance_volume(prices, volumes):
    """Calculate On-Balance Volume (OBV) - Critical for day trading liquidity."""
    if len(prices) < 2 or len(volumes) != len(prices):
        return [0] * len(prices)
    
    obv = [volumes[0]]  # Start with first volume
    
    for i in range(1, len(prices)):
        if prices[i] > prices[i-1]:  # Price up
            obv.append(obv[-1] + volumes[i])
        elif prices[i] < prices[i-1]:  # Price down
            obv.append(obv[-1] - volumes[i])
        else:  # Price unchanged
            obv.append(obv[-1])
    
    return obv

def calculate_volume_moving_average(volumes, window=20):
    """Calculate Volume Moving Average for liquidity assessment."""
    if len(volumes) < window:
        return [np.mean(volumes)] * len(volumes)
    
    vma = []
    for i in range(len(volumes)):
        if i < window - 1:
            vma.append(np.mean(volumes[:i+1]))
        else:
            vma.append(np.mean(volumes[i-window+1:i+1]))
    
    return vma

def calculate_volume_rate_of_change(volumes, period=14):
    """Calculate Volume Rate of Change (VROC) for momentum detection."""
    if len(volumes) <= period:
        return [0] * len(volumes)
    
    vroc = [0] * period
    
    for i in range(period, len(volumes)):
        if volumes[i-period] != 0:
            change = ((volumes[i] - volumes[i-period]) / volumes[i-period]) * 100
            vroc.append(change)
        else:
            vroc.append(0)
    
    return vroc

def calculate_volume_price_trend(prices, volumes):
    """Calculate Volume Price Trend (VPT) indicator."""
    if len(prices) < 2 or len(volumes) != len(prices):
        return [0] * len(prices)
    
    vpt = [0]  # Start with 0
    
    for i in range(1, len(prices)):
        if prices[i-1] != 0:
            price_change = (prices[i] - prices[i-1]) / prices[i-1]
            vpt.append(vpt[-1] + (volumes[i] * price_change))
        else:
            vpt.append(vpt[-1])
    
    return vpt

def analyze_volume_profile(prices, volumes, current_price):
    """Analyze volume profile for day trading insights."""
    if not prices or not volumes or len(prices) != len(volumes):
        return {"liquidity_score": 0, "volume_trend": "neutral", "breakout_potential": False}
    
    # Calculate indicators
    obv = calculate_on_balance_volume(prices, volumes)
    vma = calculate_volume_moving_average(volumes)
    vroc = calculate_volume_rate_of_change(volumes)
    vpt = calculate_volume_price_trend(prices, volumes)
    
    # Current metrics
    current_volume = volumes[-1]
    avg_volume = np.mean(volumes[-20:]) if len(volumes) >= 20 else np.mean(volumes)
    volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
    
    # OBV trend (last 5 periods)
    obv_trend = "up" if len(obv) >= 5 and obv[-1] > obv[-5] else "down"
    
    # Volume surge detection
    volume_surge = volume_ratio > 1.5  # 50% above average
    
    # Liquidity score (0-100)
    liquidity_score = min(100, (volume_ratio * 20) + (30 if volume_surge else 0) + (20 if obv_trend == "up" else 10))
    
    # Breakout potential
    breakout_potential = volume_surge and obv_trend == "up" and len(vroc) > 0 and vroc[-1] > 10
    
    return {
        "liquidity_score": round(liquidity_score, 2),
        "volume_trend": obv_trend,
        "volume_ratio": round(volume_ratio, 2),
        "breakout_potential": breakout_potential,
        "volume_surge": volume_surge,
        "obv_current": obv[-1] if obv else 0,
        "vpt_current": vpt[-1] if vpt else 0
    }

def enhanced_day_trading_signal(prices, volumes, rsi, macd, signal_line, ma_short, ma_long):
    """Enhanced signal generation with volume analysis for day trading."""
    if not prices or len(prices) < 2:
        return "hold", 0
    
    current_price = prices[-1]
    prev_price = prices[-2] if len(prices) > 1 else current_price
    
    # Volume analysis
    volume_analysis = analyze_volume_profile(prices, volumes, current_price)
    
    # Signal strength (0-100)
    signal_strength = 0
    signal = "hold"
    
    # Price momentum signals
    if rsi is not None and ma_short is not None and ma_long is not None:
        # RSI signals
        if 30 <= rsi <= 40:  # Oversold but not extreme
            signal_strength += 20
        elif rsi > 70:  # Overbought - potential sell
            signal_strength -= 15
        
        # Moving average signals
        if ma_short > ma_long and current_price > ma_short:  # Strong uptrend
            signal_strength += 25
        elif ma_short < ma_long:  # Downtrend
            signal_strength -= 20
    
    # MACD signals
    if macd is not None and signal_line is not None:
        if macd > signal_line and macd > 0:  # Bullish momentum
            signal_strength += 15
        elif macd < signal_line:  # Bearish momentum
            signal_strength -= 10
    
    # Volume confirmation (CRITICAL for day trading)
    liquidity_score = volume_analysis["liquidity_score"]
    volume_trend = volume_analysis["volume_trend"]
    breakout_potential = volume_analysis["breakout_potential"]
    
    # Volume boost/penalty
    if liquidity_score > 70:  # High liquidity
        signal_strength += 20
    elif liquidity_score < 30:  # Low liquidity - risky for day trading
        signal_strength -= 30
    
    if volume_trend == "up" and current_price > prev_price:  # Volume confirms price
        signal_strength += 15
    
    if breakout_potential:  # High breakout potential
        signal_strength += 25
    
    # Final signal determination
    if signal_strength >= 60:
        signal = "buy"
    elif signal_strength <= -30:
        signal = "sell"
    else:
        signal = "hold"
    
    return signal, min(100, max(0, signal_strength))

def calculate_moving_averages(data, short_window=20, long_window=50):
    """Calculate short and long moving averages."""
    data['Short_MA'] = data['Close'].rolling(window=short_window).mean()
    data['Long_MA'] = data['Close'].rolling(window=long_window).mean()
    return data

def identify_signals(data):
    """Identify buy and sell signals based on moving average crossovers."""
    data['Signal'] = 0
    data.loc[data['Short_MA'] > data['Long_MA'], 'Signal'] = 1  # Buy signal
    data.loc[data['Short_MA'] <= data['Long_MA'], 'Signal'] = -1  # Sell signal
    return data

def fetch_brapi_data(ticker, interval, range_):
    """Fetch all relevant data (market, balance sheet, historical, intraday) for a ticker from BRAPI in a single call."""
    token = os.getenv('BRAPI_API_KEY')
    if not token:
        print("Error: BRAPI_API_KEY is not set in the environment variables.")
        return None
    url = f"https://brapi.dev/api/quote/{ticker}"
    params = {
        'range': range_,
        'interval': interval,
        'fundamental': 'true',
        'dividends': 'true',
        'modules': ['balanceSheetHistory', 'defaultKeyStatistics'],
        'token': token,
    }
    try:
        response = requests.get(url, params=params)
        print(response.json())
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to fetch data for {ticker}: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None

def process_market_and_balance_sheet_data(data, ticker=None):
    """Process market, balance sheet, and historical price data. Only returns processed data, does not insert into database."""
    try:
        market_data = data['results'][0]  # Use the latest market data
        balance_sheet_data = None
        if 'balanceSheetHistory' in data['results'][0] and data['results'][0]['balanceSheetHistory']:
            balance_sheet_data = data['results'][0]['balanceSheetHistory'][0]
        historical_data = data['results'][0]['historicalDataPrice']

        # Extract relevant market data 
        market_info = {
            'symbol': market_data['symbol'],
            'regularMarketPrice': market_data['regularMarketPrice'],
            'regularMarketVolume': market_data['regularMarketVolume'],
            'fiftyTwoWeekRange': market_data['fiftyTwoWeekRange'],
            'priceEarnings': market_data.get('priceEarnings'),
            'earningsPerShare': market_data.get('earningsPerShare')
        }

        # Extract relevant balance sheet data
        balance_sheet_info = None
        if balance_sheet_data:
            balance_sheet_info = {
                'endDate': balance_sheet_data['endDate'],
                'totalCurrentAssets': balance_sheet_data['totalCurrentAssets'],
                'totalCurrentLiabilities': balance_sheet_data['totalCurrentLiabilities'],
                'totalLiab': balance_sheet_data['totalLiab'],
                'totalStockholderEquity': balance_sheet_data['totalStockholderEquity']
            }

        # Extract relevant historical price data
        historical_prices = [
            {
                'date': hp['date'],
                'open': hp['open'],
                'high': hp['high'],
                'low': hp['low'],
                'close': hp['close'],
                'volume': hp['volume'],
                'adjustedClose': hp['adjustedClose']
            }
            for hp in historical_data
        ]

        # Map ticker if needed (e.g., '^BVSP' to 'IBOV')
        mapped_ticker = 'IBOV' if ticker == '^BVSP' else ticker
        for price in historical_prices:
            save_historical_prices((
                mapped_ticker,
                price['date'],
                price['open'],
                price['high'],
                price['low'],
                price['close'],
                price['volume'],
                price['adjustedClose']
            ))

        # No database inserts here!
        return market_info, balance_sheet_info, historical_prices
    except KeyError as e:
        print(f"Missing key in data: {e}")
        return None, None, None

def calculate_financial_ratios(balance_sheet_data):
    """Calculate financial ratios from balance sheet data."""
    try:
        current_ratio = balance_sheet_data['totalCurrentAssets'] / balance_sheet_data['totalCurrentLiabilities']
        debt_to_equity_ratio = balance_sheet_data['totalLiab'] / balance_sheet_data['totalStockholderEquity']
        return {
            'current_ratio': current_ratio,
            'debt_to_equity_ratio': debt_to_equity_ratio
        }
    except KeyError as e:
        print(f"Missing key in balance sheet data: {e}")
        return {}

def prepare_features_and_labels(data, market_info, financial_ratios):
    """Prepare features and labels for machine learning."""
    features = []
    labels = []

    for row in data:
        features.append([
            row['regularMarketPrice'],
            row['regularMarketVolume'],
            financial_ratios.get('current_ratio', 0),
            financial_ratios.get('debt_to_equity_ratio', 0)
        ])
        labels.append(1 if row['regularMarketPrice'] > row['regularMarketOpen'] else 0)  # 1 for profit, 0 for loss

    return features, labels

def train_model(features, labels):
    """Train a machine learning model to predict the best asset."""
    X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.2, random_state=42)

    model = RandomForestClassifier(random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model Accuracy: {accuracy:.2f}")

    # Save the trained model
    joblib.dump(model, 'daytrade_model.pkl')
    return model

def predict_best_asset(model, features, tickers):
    """Predict the best asset for day trading."""
    predictions = model.predict(features)
    probabilities = model.predict_proba(features)[:, 1]  # Probability of class 1 (profit)

    best_asset_index = probabilities.argmax()
    best_asset = tickers[best_asset_index]
    print(f"Best asset to trade: {best_asset}")
    return best_asset

def calculate_stop_loss_take_profit_levels(historical_prices):
    """Calculate stop-loss and take-profit levels based on historical prices."""
    lowest_low = min(hp['low'] for hp in historical_prices)
    highest_high = max(hp['high'] for hp in historical_prices)

    stop_loss = lowest_low * 0.99  # Slightly below the lowest low
    take_profit = highest_high * 1.01  # Slightly above the highest high

    return stop_loss, take_profit

def calculate_position_size(account_balance, risk_per_trade, stop_loss, current_price):
    """Calculate the position size based on account balance, risk, and stop-loss distance."""
    risk_amount = account_balance * risk_per_trade
    stop_loss_distance = current_price - stop_loss
    if stop_loss_distance <= 0:
        raise ValueError("Stop-loss distance must be positive.")
    position_size = risk_amount / stop_loss_distance
    return position_size

def apply_stop_loss_take_profit(current_price, stop_loss, take_profit):
    """Check if stop-loss or take-profit conditions are met."""
    if current_price <= stop_loss:
        return "stop_loss"
    elif current_price >= take_profit:
        return "take_profit"
    return None

def save_financial_data_to_db(ticker, balance_sheet_info, financial_ratios):
    """Save balance sheet data and financial ratios to the database."""
    try:
        save_balance_sheet_data((
            ticker,
            balance_sheet_info['endDate'],
            balance_sheet_info['totalCurrentAssets'],
            balance_sheet_info['totalCurrentLiabilities'],
            balance_sheet_info['totalLiab'],
            balance_sheet_info['totalStockholderEquity'],
            financial_ratios.get('current_ratio'),
            financial_ratios.get('debt_to_equity_ratio')
        ))
        print(f"Saved financial data for {ticker} to the database.")
    except Exception as e:
        print(f"Failed to save financial data for {ticker}: {e}")

def calculate_rsi(prices, period=14):
    """Calculate the Relative Strength Index (RSI)."""
    deltas = np.diff(prices)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)

    avg_gain = np.convolve(gains, np.ones(period) / period, mode='valid')
    avg_loss = np.convolve(losses, np.ones(period) / period, mode='valid')

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return np.concatenate((np.full(period - 1, np.nan), rsi))

def calculate_macd(prices, short_period=12, long_period=26, signal_period=9):
    """Calculate MACD and Signal Line."""
    short_ema = pd.Series(prices).ewm(span=short_period, adjust=False).mean()
    long_ema = pd.Series(prices).ewm(span=long_period, adjust=False).mean()

    macd = short_ema - long_ema
    signal_line = macd.ewm(span=signal_period, adjust=False).mean()

    return macd, signal_line

def calculate_beta_from_returns(asset_ticker, market_ticker, lookback_days=60):
    """
    Calculate beta using linear regression on historical returns for asset and market index.
    Returns beta or None if data is insufficient.
    """
    from utils.database import fetch_historical_prices
    import pandas as pd
    import numpy as np
    from sklearn.linear_model import LinearRegression

    # Fetch historical prices from the database
    asset_prices = fetch_historical_prices(asset_ticker)
    market_prices = fetch_historical_prices(market_ticker)

    if not asset_prices or not market_prices:
        print(f"Insufficient price data for {asset_ticker} or {market_ticker}.")
        return None

    # Convert to DataFrame and sort by date ascending
    asset_df = pd.DataFrame(asset_prices)
    market_df = pd.DataFrame(market_prices)
    asset_df['date'] = pd.to_datetime(asset_df['date'])
    market_df['date'] = pd.to_datetime(market_df['date'])
    asset_df = asset_df.sort_values('date').tail(lookback_days)
    market_df = market_df.sort_values('date').tail(lookback_days)

    # Merge on date to align
    merged = pd.merge(asset_df[['date', 'close']], market_df[['date', 'close']], on='date', suffixes=('_asset', '_market'))
    if len(merged) < 2:
        print("Not enough overlapping data to calculate beta.")
        return None

    # Calculate daily returns
    merged['asset_return'] = merged['close_asset'].pct_change()
    merged['market_return'] = merged['close_market'].pct_change()
    merged = merged.dropna(subset=['asset_return', 'market_return'])
    if len(merged) < 2:
        print("Not enough return data to calculate beta.")
        return None    # Linear regression: asset_return = alpha + beta * market_return
    X = np.array(merged['market_return']).reshape(-1, 1)
    y = np.array(merged['asset_return'])
    reg = LinearRegression().fit(X, y)
    beta = reg.coef_[0]
    return beta

def map_ticker_for_db(ticker):
    """Map API tickers to database-friendly tickers."""
    return 'IBOV' if ticker == '^BVSP' else ticker

def run_technical_analysis():
    tickers = ["^BVSP","PETR4", "VALE3", "ITUB4", "AMER3", "B3SA3", "MGLU3", "LREN3", "ITSA4", "BBAS3", "RENT3", "ABEV3", "SUZB3", "WEG3", "BRFS3", "BBDC4", "CRFB3", "BPAC11", "GGBR3", "EMBR3", "CMIN3", "ITSA4", "RDOR3", "RAIZ4", "PETZ3", "PSSA3", "VBBR3"]

    all_features = []
    all_labels = []

    for ticker in tickers:
        db_ticker = map_ticker_for_db(ticker)
        print(f"Fetching all BRAPI data for {ticker}...")
        
        try:
            market_data = fetch_brapi_data(ticker, interval='1d', range_='1mo')

            if market_data:
                print(f"Processing data for {ticker}...")
                market_info, balance_sheet_info, historical_prices = process_market_and_balance_sheet_data(market_data, ticker)

                if market_info and balance_sheet_info and historical_prices:
                    print(f"Calculating financial ratios for {ticker}...")
                    financial_ratios = calculate_financial_ratios(balance_sheet_info)

                    print(f"Saving financial data for {db_ticker} to the database...")
                    save_balance_sheet_data((
                        db_ticker,
                        balance_sheet_info['endDate'],
                        balance_sheet_info['totalCurrentAssets'],
                        balance_sheet_info['totalCurrentLiabilities'],
                        balance_sheet_info['totalLiab'],
                        balance_sheet_info['totalStockholderEquity'],
                        financial_ratios.get('current_ratio'),
                        financial_ratios.get('debt_to_equity_ratio')
                    ))

                    print(f"Saving historical prices for {db_ticker} to the database...")
                    for price in historical_prices:
                        save_historical_prices((
                            db_ticker,
                            price['date'],
                            price['open'],
                            price['high'],
                            price['low'],
                            price['close'],
                            price['volume'],
                            price['adjustedClose']
                        ))

                    print(f"Saving daily analysis for {db_ticker} to the database...")
                    close_prices = [p['close'] for p in historical_prices]
                    if not close_prices or any(c is None for c in close_prices):
                        print(f"Skipping {ticker}: insufficient close price data.")
                        continue  # Skip this ticker if data is missing
                    # Calculate RSI, MACD, and Signal Line
                    rsi_values = calculate_rsi(close_prices)
                    macd_values, signal_line_values = calculate_macd(close_prices)
                    
                    tickers_with_data = []

                    for i, price in enumerate(historical_prices):
                        # Calculate short_ma and long_ma using moving averages
                        short_ma = sum(close_prices[max(0, i-2):i+1]) / min(3, i+1)  # Example: 3-period moving average
                        long_ma = sum(close_prices[:i+1]) / (i+1)  # Example: cumulative moving average

                        rsi = rsi_values[i] if i < len(rsi_values) else None
                        macd = macd_values[i] if i < len(macd_values) else None
                        signal_line = signal_line_values[i] if i < len(signal_line_values) else None

                        insert_daily_analysis((
                            price['date'],
                            price['close'],
                            short_ma,
                            long_ma,
                            rsi,
                            macd,
                            signal_line,
                            db_ticker
                        ))

                    print(f"Saving yearly analysis for {db_ticker} to the database...")
                    insert_yearly_analysis((
                        historical_prices[0]['date'],  # Most recent date
                        historical_prices[0]['close'],  # Most recent close price
                        db_ticker,
                    ))

                    print(f"Analyzing asset for {db_ticker}...")
                    # Check if defaultKeyStatistics exists in the API response
                    default_key_stats = market_data['results'][0].get('defaultKeyStatistics', {})
                    if default_key_stats:
                        asset_analysis = analyze_asset(default_key_stats, market_info['regularMarketPrice'])
                        insert_asset_analysis((
                            db_ticker,
                            asset_analysis['forward_pe'],
                            asset_analysis['profit_margins'],
                            asset_analysis['beta'],
                            asset_analysis['dividend_yield'],
                            asset_analysis['peg_ratio']
                        ))
                    else:
                        print(f"Warning: defaultKeyStatistics not available for {ticker}. Using default values.")
                        # Insert default values to maintain database consistency
                        insert_asset_analysis((
                            db_ticker,
                            "Data Not Available",  # forward_pe
                            "Data Not Available",  # profit_margins
                            "Data Not Available",  # beta
                            0.0,                   # dividend_yield (numeric default)
                            "Data Not Available"   # peg_ratio
                        ))

                    print(f"Preparing features and labels for {ticker}...")
                    features, labels = prepare_features_and_labels(market_data['results'], market_info, financial_ratios)
                    all_features.extend(features)
                    all_labels.extend(labels)

                    if features and labels:
                        tickers_with_data.append(db_ticker)
                        print(f"Tickers with data: {tickers_with_data}")
                else:
                    print(f"Warning: Incomplete data for {ticker}. Skipping.")
            else:
                print(f"Warning: No market data received for {ticker}. Skipping.")
                
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            print(f"Continuing with next ticker...")
            continue
    print(f"Total features collected: {len(all_features)}")
    print(f"Total labels collected: {len(all_labels)}")

    if not all_features or not all_labels:
        print("No data available for training. Skipping model training.")
        return None
    print("Training the model...")
    model = train_model(all_features, all_labels)
    
    print("Predicting the best asset for day trading...")
    best_asset = predict_best_asset(model, all_features, tickers)
    return best_asset