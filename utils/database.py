import os
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime, timezone
import numpy as np

# Load environment variables
load_dotenv()

"""Initialize the PostgreSQL database and create tables."""
SUPABASE_URL = os.getenv("DATABASE_URL")
SUPABASE_KEY = os.getenv("DATABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def safe_check_nan(value):
    """Check if a value is NaN, safely handling non-numeric types."""
    if isinstance(value, (int, float, np.float64)):
        return np.isnan(value)
    return False

def insert_daily_analysis(data):
    """Insert data into the daily_analysis table, avoiding duplicates by ticker and date."""
    date, close_price, short_ma, long_ma, rsi, macd, signal_line, ticker = data
    date = datetime.fromtimestamp(date, tz=timezone.utc).strftime('%Y-%m-%d')

    # Check for existing entry
    existing = supabase.table("daily_analysis").select("id").eq("ticker", ticker).eq("date", date).execute()
    if existing.data and len(existing.data) > 0:
        print(f"Daily analysis for {ticker} on {date} already exists. Skipping insert.")
        return

    close_price = None if safe_check_nan(close_price) else close_price
    short_ma = None if safe_check_nan(short_ma) else short_ma
    long_ma = None if safe_check_nan(long_ma) else long_ma
    rsi = None if safe_check_nan(rsi) else rsi
    macd = None if safe_check_nan(macd) else macd
    signal_line = None if safe_check_nan(signal_line) else signal_line

    result = supabase.table("daily_analysis").insert(
        {"date": date, 
         "close_price": close_price, 
         "short_ma": short_ma, 
         "long_ma": long_ma, 
         "rsi": rsi, 
         "macd": macd, 
         "signal_line": signal_line, 
         "ticker": ticker, 
         "user_id": os.getenv("USER_ID")}).execute()
    
    if result:
        print(f"Inserted daily analysis data for {date}")
    else:
        print(f"Failed to insert daily analysis data for {date}")

def insert_yearly_analysis(data):
    """Insert data into the yearly_analysis table, avoiding duplicates by ticker and date."""
    date, close_price, ticker = data
    date = datetime.fromtimestamp(date, tz=timezone.utc).strftime('%Y-%m-%d')
    existing = supabase.table("yearly_analysis").select("id").eq("ticker", ticker).eq("date", date).execute()
    if existing.data and len(existing.data) > 0:
        print(f"Yearly analysis for {ticker} on {date} already exists. Skipping insert.")
        return
    result = supabase.table("yearly_analysis").insert(
        {"date": date, "close_price": close_price, "ticker": ticker, "user_id": os.getenv("USER_ID")}).execute()
    
    if result:
        print(f"Inserted yearly analysis data for {date}")
    else:
        print(f"Failed to insert yearly analysis data for {date}")

def save_balance_sheet_data(data):
    """Save balance sheet data and financial ratios to the database."""
    ticker, end_date, total_current_assets, total_current_liabilities, total_liabilities, total_stockholder_equity, current_ratio, debt_to_equity_ratio = data

    existing = supabase.table("balance_sheet").select("id").eq("ticker", ticker).eq("end_date", end_date).execute()

    if existing.data and len(existing.data) > 0:
        print(f"Balance sheet data for {ticker} on {end_date} already exists. Skipping insert.")
        return

    result = supabase.table("balance_sheet").insert(
        {
            "ticker": ticker,
            "end_date": end_date,
            "total_current_assets": total_current_assets,
            "total_current_liabilities": total_current_liabilities,
            "total_liabilities": total_liabilities,
            "total_stockholder_equity": total_stockholder_equity,
            "current_ratio": current_ratio,
            "debt_to_equity_ratio": debt_to_equity_ratio,
            "user_id": os.getenv("USER_ID")
        }
    ).execute()

    if result:
        print(f"Inserted balance sheet data for {ticker} on {end_date}")
    else:
        print(f"Failed to insert balance sheet data for {ticker} on {end_date}")


def save_historical_prices(data):
    """Save historical prices to the database, avoiding duplicates by ticker and date."""
    ticker, date, open_price, high_price, low_price, close_price, volume, adjusted_close = data
    date = datetime.fromtimestamp(date, tz=timezone.utc).strftime('%Y-%m-%d')
    existing = supabase.table("historical_prices").select("id").eq("ticker", ticker).eq("date", date).execute()
    if existing.data and len(existing.data) > 0:
        print(f"Historical price for {ticker} on {date} already exists. Skipping insert.")
        return
    result = supabase.table("historical_prices").insert(
        {"ticker": ticker, "date": date, "open": open_price, "high": high_price, "low": low_price, "close": close_price, "volume": volume, "adjusted_close": adjusted_close, "user_id": os.getenv("USER_ID")}).execute()
    
    if result:
        print(f"Inserted historical price data for {ticker} on {date}")
    else:
        print(f"Failed to insert historical price data for {ticker} on {date}")

def insert_asset_analysis(data):
    """Insert analysis results into the asset_analysis table."""
    ticker, forward_pe, profit_margins, beta, dividend_yield, peg_ratio = data
    result = supabase.table("asset_analysis").insert({
        "ticker": ticker,
        "forward_pe": forward_pe,
        "profit_margins": profit_margins,
        "beta": beta,
        "dividend_yield": dividend_yield,
        "peg_ratio": peg_ratio,
        "user_id": os.getenv("USER_ID")
    }).execute()

    if result:
        print(f"Inserted asset analysis data for {ticker}.")
    else:
        print(f"Failed to insert asset analysis data for {ticker}")


def insert_finance_metrics(data):
    """Insert finance metrics into the finance_metrics table."""
    ticker, roe, roa, revenue_growth, operating_cashflow, free_cashflow, current_ratio, debt_to_equity, profit_margins, gross_margins, ebitda_margins, operating_margins, operating_cashflow_ratio, free_cash_flow_ratio = data
    result = supabase.table("finance_metrics").insert({
        "ticker": ticker,
        "roe": roe,
        "roa": roa,
        "revenue_growth": revenue_growth,
        "operating_cashflow": operating_cashflow,
        "free_cashflow": free_cashflow,
        "current_ratio": current_ratio,
        "debt_to_equity": debt_to_equity,
        "profit_margins": profit_margins,
        "gross_margins": gross_margins,
        "ebitda_margins": ebitda_margins,
        "operating_margins": operating_margins,
        "operating_cashflow_ratio": operating_cashflow_ratio,
        "free_cash_flow_ratio": free_cash_flow_ratio,
        "user_id": os.getenv("USER_ID")
    }).execute()

    if result:
        print(f"Inserted finance metrics data for {ticker}.")
    else:
        print(f"Failed to insert finance metrics data for {ticker}")

def insert_intraday_prices(data):
    """Insert intraday prices into the intraday_prices table."""
    ticker, date, open_price, high_price, low_price, close_price, volume, adjusted_close = data
    date = datetime.fromtimestamp(date, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    existing = supabase.table("intraday_prices").select("id").eq("ticker", ticker).eq("date", date).execute()
    if existing.data and len(existing.data) > 0:
        print(f"Intraday price for {ticker} on {date} already exists. Skipping insert.")
        return
    result = supabase.table("intraday_prices").insert(
        {"ticker": ticker, "date": date, "open": open_price, "high": high_price, "low": low_price, "close": close_price, "volume": volume, "adjusted_close": adjusted_close, 
        "user_id": os.getenv("USER_ID")}).execute()
    
    if result:
        print(f"Inserted intraday price data for {ticker} on {date}")
    else:
        print(f"Failed to insert intraday price data for {ticker} on {date}")

def insert_trade_asset(data):
    """Insert trade asset data into the trade_asset table."""
    ticker, type, price, volume = data
    result = supabase.table("trade_asset").insert(
        {"ticker": ticker, "type": type, "price": price, "volume": volume, "user_id": os.getenv("USER_ID")}).execute()
    
    if result:
        print(f"Inserted trade asset data for {ticker} per {price}")
    else:
        print(f"Failed to insert trade asset data for {ticker} per {price}")

def fetch_trade_asset(ticker):
    """Fetch trade asset data for a given ticker from the database."""
    data = supabase.table("trade_asset").select(
        "id, ticker, type, price, volume"
    ).eq("ticker", ticker).order("created_at", desc=True).execute()

    if data.data:
        return data.data
    else:
        print(f"Failed to fetch trade asset data for {ticker}")
        return None

def fetch_intraday_prices(ticker):
    """Fetch intraday prices for a given ticker from the database."""
    data = supabase.table("intraday_prices").select(
        "id, ticker, date, open, high, low, close, volume, adjusted_close"
    ).eq("ticker", ticker).order("date", desc=True).execute()

    if data.data:
        return data.data
    else:
        print(f"Failed to fetch intraday prices for {ticker}")
        return None
    
def fetch_finance_metrics(ticker):
    """Fetch finance metrics for a given ticker from the database."""
    data = supabase.table("finance_metrics").select(
        "id, ticker, roe, roa, revenue_growth, operating_cashflow, free_cashflow, current_ratio, debt_to_equity, profit_margins, gross_margins, ebitda_margins, operating_margins, operating_cashflow_ratio, free_cash_flow_ratio"
    ).eq("ticker", ticker).order("created_at", desc=True).execute()

    if data.data:
        return data.data
    else:
        print(f"Failed to fetch finance metrics for {ticker}")
        return None

def fetch_balance_sheet_data(ticker):
    """Fetch balance sheet data and financial ratios for a given ticker from the database."""
    data = supabase.table("balance_sheet").select(
        "id, ticker, end_date, total_current_assets, total_current_liabilities, total_liabilities, total_stockholder_equity, current_ratio, debt_to_equity_ratio"
    ).eq("ticker", ticker).order("end_date", desc=True).execute()

    if data.data:
        return data.data
    else:
        print(f"Failed to fetch balance sheet data for {ticker}")
        return None

def fetch_historical_prices(ticker):
    """Fetch historical prices for a given ticker from the database."""
    data = supabase.table("historical_prices").select(
        "id, ticker, date, open, high, low, close, volume, adjusted_close"
    ).eq("ticker", ticker).order("date", desc=True).execute()

    if data.data:
        return data.data
    else:
        print(f"Failed to fetch historical prices for {ticker}")
        return None

def fetch_daily_analysis(ticker):
    """Fetch daily analysis data for a given ticker from the database."""
    data = supabase.table("daily_analysis").select(
        "id, date, close_price, short_ma, long_ma, rsi, macd, signal_line"
    ).eq("ticker", ticker).order("date", desc=True).execute()

    if data.data:
        return data.data
    else:
        print(f"Failed to fetch daily analysis data for {ticker}")
        return None

def fetch_yearly_analysis(ticker):
    """Fetch yearly analysis data for a given ticker from the database."""
    data = supabase.table("yearly_analysis").select(
        "id, date, close_price, ticker"
    ).eq("ticker", ticker).order("date", desc=True).execute()

    if data.data:
        return data.data
    else:
        print(f"Failed to fetch yearly analysis data for {ticker}")
        return None

def fetch_asset_analysis(ticker):
    """Fetch analysis results for a specific ticker from the asset_analysis table."""
    result = supabase.table("asset_analysis").select(
        "ticker, forward_pe, profit_margins, beta, dividend_yield, peg_ratio"
    ).eq("ticker", ticker).order("created_at", desc=True).execute()

    if result.data:
        return result.data
    else:
        print(f"Failed to fetch asset analysis data for {ticker}")
        return None

def fetch_user_balance(user_id=None):
    """Fetch the most recent account balance for a user."""
    user_id = user_id or os.getenv("USER_ID")
    try:
        result = supabase.table("account_balance").select(
            "balance, updated_at, source"
        ).eq("user_id", user_id).order("updated_at", desc=True).limit(1).execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]
        else:
            print(f"No balance record found for user {user_id}")
            return None
    except Exception as e:
        print(f"Error fetching user balance: {e}")
        return None

def insert_balance_record(balance, source, user_id=None):
    """Insert a new account balance record."""
    user_id = user_id or os.getenv("USER_ID")
    try:
        result = supabase.table("account_balance").insert({
            "user_id": user_id,
            "balance": balance,
            "source": source,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }).execute()
        
        if result:
            print(f"Inserted balance record: R${balance:,.2f} (source: {source})")
            return True
        else:
            print(f"Failed to insert balance record")
            return False
    except Exception as e:
        print(f"Error inserting balance record: {e}")
        return False

def calculate_account_balance_from_trades(user_id=None, initial_balance=500.0):
    """
    Calculate current account balance based on complete trade history.
    
    This function provides a reliable balance calculation by analyzing all trades
    and calculating the running balance including realized P&L.
    """
    user_id = user_id or os.getenv("USER_ID")
    try:
        # Fetch all trades ordered by creation time
        result = supabase.table("trade_asset").select(
            "ticker, type, price, volume, created_at"
        ).eq("user_id", user_id).order("created_at", desc=False).execute()
        
        if not result.data:
            print(f"No trades found for user {user_id}, returning initial balance: R${initial_balance:,.2f}")
            return {
                'success': True,
                'balance': initial_balance,
                'trade_count': 0,
                'total_invested': 0.0,
                'total_realized': 0.0,
                'net_pnl': 0.0,
                'positions': {}
            }
        
        running_balance = initial_balance
        total_invested = 0.0
        total_realized = 0.0
        position_tracking = {}
        
        print(f"📊 Calculating balance from {len(result.data)} trades...")
        
        for trade in result.data:
            ticker = trade['ticker']
            trade_type = trade['type']
            price = float(trade['price'])
            volume = float(trade['volume'])
            
            if ticker not in position_tracking:
                position_tracking[ticker] = {
                    'shares': 0,
                    'total_cost': 0.0,
                    'realized_pnl': 0.0
                }
            
            if trade_type == 'buy':
                # Buy: Reduce balance, increase position
                cost = price * volume
                running_balance -= cost
                total_invested += cost
                
                position_tracking[ticker]['shares'] += volume
                position_tracking[ticker]['total_cost'] += cost
                
                print(f"  BUY: {ticker} {volume} @ R${price:.2f} = R${cost:.2f} | Balance: R${running_balance:.2f}")
                
            elif trade_type in ['sell', 'force_close']:
                # Sell: Increase balance, reduce position
                proceeds = price * volume
                running_balance += proceeds
                total_realized += proceeds
                
                # Calculate realized P&L for this sale
                if position_tracking[ticker]['shares'] > 0:
                    avg_cost = position_tracking[ticker]['total_cost'] / position_tracking[ticker]['shares']
                    shares_sold = min(volume, position_tracking[ticker]['shares'])
                    realized_pnl = (price - avg_cost) * shares_sold
                    
                    position_tracking[ticker]['realized_pnl'] += realized_pnl
                    position_tracking[ticker]['shares'] -= shares_sold
                    position_tracking[ticker]['total_cost'] -= avg_cost * shares_sold
                    
                    print(f"  SELL: {ticker} {volume} @ R${price:.2f} = R${proceeds:.2f} | P&L: R${realized_pnl:.2f} | Balance: R${running_balance:.2f}")
                else:
                    print(f"  SELL: {ticker} {volume} @ R${price:.2f} = R${proceeds:.2f} | Balance: R${running_balance:.2f}")
        
        net_pnl = total_realized - total_invested
        
        balance_summary = {
            'success': True,
            'balance': running_balance,
            'trade_count': len(result.data),
            'total_invested': total_invested,
            'total_realized': total_realized,
            'net_pnl': net_pnl,
            'positions': position_tracking,
            'return_percentage': ((running_balance - initial_balance) / initial_balance) * 100
        }
        
        print(f"💰 Balance Calculation Complete:")
        print(f"   Current Balance: R${running_balance:,.2f}")
        print(f"   Total Trades: {len(result.data)}")
        print(f"   Net P&L: R${net_pnl:,.2f}")
        print(f"   Return: {balance_summary['return_percentage']:.2f}%")
        
        return balance_summary
        
    except Exception as e:
        print(f"Error calculating balance from trades: {e}")
        return {
            'success': False,
            'error': str(e),
            'balance': initial_balance
        }

def get_daily_trade_summary(user_id=None, date=None):
    """Get summary of trades for a specific date."""
    user_id = user_id or os.getenv("USER_ID")
    date = date or datetime.now().strftime('%Y-%m-%d')
    
    try:
        # Fetch trades for the specific date
        result = supabase.table("trade_asset").select(
            "ticker, type, price, volume, created_at"
        ).eq("user_id", user_id).gte("created_at", f"{date}T00:00:00").lt("created_at", f"{date}T23:59:59").execute()
        
        if not result.data:
            return {
                'date': date,
                'trade_count': 0,
                'total_volume': 0.0,
                'total_value': 0.0,
                'buy_count': 0,
                'sell_count': 0,
                'tickers_traded': []
            }
        
        buy_count = 0
        sell_count = 0
        total_value = 0.0
        total_volume = 0.0
        tickers_traded = set()
        
        for trade in result.data:
            ticker = trade['ticker']
            trade_type = trade['type']
            price = float(trade['price'])
            volume = float(trade['volume'])
            
            tickers_traded.add(ticker)
            total_volume += volume
            total_value += price * volume
            
            if trade_type == 'buy':
                buy_count += 1
            elif trade_type in ['sell', 'force_close']:
                sell_count += 1
        
        return {
            'date': date,
            'trade_count': len(result.data),
            'total_volume': total_volume,
            'total_value': total_value,
            'buy_count': buy_count,
            'sell_count': sell_count,
            'tickers_traded': list(tickers_traded)
        }
        
    except Exception as e:
        print(f"Error getting daily trade summary: {e}")
        return None
