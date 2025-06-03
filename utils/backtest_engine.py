"""
Comprehensive Backtesting Engine for the Trading Robot
Simulates historical trading performance using the same logic as the live robot.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from utils.database import fetch_historical_prices, fetch_daily_analysis
from utils.technical_analysis import calculate_rsi, calculate_macd, calculate_stop_loss_take_profit_levels, calculate_position_size, apply_stop_loss_take_profit
from utils.quick_technical_analysis import get_price_signals
import matplotlib.pyplot as plt
import json
import os

class BacktestEngine:
    def __init__(self, initial_balance=1000, risk_per_trade=0.02, start_date=None, end_date=None):
        """
        Initialize the backtesting engine
        
        Args:
            initial_balance (float): Starting account balance
            risk_per_trade (float): Risk percentage per trade (0.02 = 2%)
            start_date (str): Start date for backtesting (YYYY-MM-DD)
            end_date (str): End date for backtesting (YYYY-MM-DD)
        """
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        self.risk_per_trade = risk_per_trade
        self.start_date = start_date
        self.end_date = end_date
        
        # Trading state
        self.position = None
        self.position_size = 0
        self.entry_price = 0
        self.stop_loss = 0
        self.take_profit = 0
        
        # Performance tracking
        self.trades = []
        self.equity_curve = []
        self.daily_returns = []
        
        # Tickers to test
        self.tickers = [
            "PETR4", "VALE3", "ITUB4", "AMER3", "B3SA3", "MGLU3", "LREN3", 
            "ITSA4", "BBAS3", "RENT3", "ABEV3", "SUZB3", "WEG3", "BRFS3", 
            "BBDC4", "CRFB3", "BPAC11", "GGBR3", "EMBR3", "CMIN3"
        ]

    def prepare_historical_data(self, ticker):
        """Prepare historical data for backtesting"""
        print(f"Preparing historical data for {ticker}...")
        
        # Fetch historical prices from database
        historical_prices = fetch_historical_prices(ticker)
        if not historical_prices:
            print(f"No historical data found for {ticker}")
            return None
            
        # Convert to DataFrame
        df = pd.DataFrame(historical_prices)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # Filter by date range if specified
        if self.start_date:
            df = df[df['date'] >= self.start_date]
        if self.end_date:
            df = df[df['date'] <= self.end_date]
            
        if len(df) < 20:  # Need minimum data for technical indicators
            print(f"Insufficient data for {ticker}")
            return None
            
        return df

    def calculate_technical_indicators(self, df):
        """Calculate technical indicators for the data"""
        close_prices = df['close'].values
        
        # Calculate RSI
        rsi_values = calculate_rsi(close_prices, period=14)
        
        # Calculate MACD
        macd_values, signal_line_values = calculate_macd(close_prices)
        
        # Add to dataframe
        df['rsi'] = rsi_values
        df['macd'] = macd_values
        df['signal_line'] = signal_line_values
        
        # Calculate moving averages
        df['ma_short'] = df['close'].rolling(window=10).mean()
        df['ma_long'] = df['close'].rolling(window=20).mean()
        
        return df

    def generate_trading_signal(self, current_data, historical_data):
        """
        Generate trading signal using the same logic as the live robot
        
        Args:
            current_data: Current day's data
            historical_data: Historical data up to current point
            
        Returns:
            str: 'buy', 'sell', or 'hold'
        """
        current_rsi = current_data.get('rsi')
        current_price = current_data.get('close')
        ma_short = current_data.get('ma_short')
        ma_long = current_data.get('ma_long')
        
        # Skip if indicators are not available
        if pd.isna(current_rsi) or pd.isna(ma_short) or pd.isna(ma_long):
            return 'hold'
        
        # Buy signals
        if (current_rsi < 40 and  # Oversold but not extreme
            ma_short > ma_long and  # Uptrend
            current_price > ma_short):  # Price above short MA
            return 'buy'
            
        # Sell signals
        if (current_rsi > 60 or  # Overbought
            ma_short < ma_long):  # Downtrend
            return 'sell'
            
        return 'hold'

    def execute_trade(self, signal, current_data, date):
        """Execute a trade based on the signal"""
        current_price = current_data['close']
        
        if signal == 'buy' and self.position is None:
            # Calculate position size
            # Use simplified stop loss for backtesting (5% below current price)
            stop_loss = current_price * 0.95
            position_size = calculate_position_size(
                self.current_balance, 
                self.risk_per_trade, 
                stop_loss, 
                current_price
            )
            
            # Ensure we don't exceed available balance
            max_position = self.current_balance / current_price
            position_size = min(position_size, max_position)
            
            if position_size > 0:
                self.position = 'long'
                self.position_size = position_size
                self.entry_price = current_price
                self.stop_loss = stop_loss
                self.take_profit = current_price * 1.10  # 10% profit target
                
                # Record trade
                trade = {
                    'date': date,
                    'type': 'buy',
                    'ticker': current_data.get('ticker', 'UNKNOWN'),
                    'price': current_price,
                    'size': position_size,
                    'balance_before': self.current_balance
                }
                self.trades.append(trade)
                
                print(f"BUY: {position_size:.2f} shares at {current_price:.2f} on {date}")
                
        elif signal == 'sell' and self.position == 'long':
            # Close position
            proceeds = self.position_size * current_price
            self.current_balance = proceeds
            
            # Calculate P&L
            pnl = proceeds - (self.position_size * self.entry_price)
            pnl_percent = (current_price - self.entry_price) / self.entry_price * 100
            
            # Record trade
            trade = {
                'date': date,
                'type': 'sell',
                'ticker': current_data.get('ticker', 'UNKNOWN'),
                'price': current_price,
                'size': self.position_size,
                'pnl': pnl,
                'pnl_percent': pnl_percent,
                'balance_after': self.current_balance
            }
            self.trades.append(trade)
            
            print(f"SELL: {self.position_size:.2f} shares at {current_price:.2f} on {date}, P&L: {pnl:.2f} ({pnl_percent:.2f}%)")
            
            # Reset position
            self.position = None
            self.position_size = 0
            self.entry_price = 0

    def check_stop_loss_take_profit(self, current_data, date):
        """Check if stop loss or take profit should be triggered"""
        if self.position is None:
            return
            
        current_price = current_data['close']
        
        # Check stop loss and take profit
        sl_tp_signal = apply_stop_loss_take_profit(current_price, self.stop_loss, self.take_profit)
        
        if sl_tp_signal in ['stop_loss', 'take_profit']:
            # Force close position
            proceeds = self.position_size * current_price
            self.current_balance = proceeds
            
            # Calculate P&L
            pnl = proceeds - (self.position_size * self.entry_price)
            pnl_percent = (current_price - self.entry_price) / self.entry_price * 100
            
            # Record trade
            trade = {
                'date': date,
                'type': f'sell_{sl_tp_signal}',
                'ticker': current_data.get('ticker', 'UNKNOWN'),
                'price': current_price,
                'size': self.position_size,
                'pnl': pnl,
                'pnl_percent': pnl_percent,
                'balance_after': self.current_balance
            }
            self.trades.append(trade)
            
            print(f"{sl_tp_signal.upper()}: {self.position_size:.2f} shares at {current_price:.2f} on {date}, P&L: {pnl:.2f} ({pnl_percent:.2f}%)")
            
            # Reset position
            self.position = None
            self.position_size = 0
            self.entry_price = 0

    def backtest_single_ticker(self, ticker):
        """Run backtest for a single ticker"""
        print(f"\n=== Backtesting {ticker} ===")
        
        # Prepare data
        df = self.prepare_historical_data(ticker)
        if df is None:
            return
            
        # Calculate technical indicators
        df = self.calculate_technical_indicators(df)
        
        # Add ticker to data
        df['ticker'] = ticker
        
        # Simulate trading day by day
        for i in range(20, len(df)):  # Start after we have enough data for indicators
            current_data = df.iloc[i].to_dict()
            date = current_data['date']
            
            # Check stop loss/take profit first
            self.check_stop_loss_take_profit(current_data, date)
            
            # Generate signal
            signal = self.generate_trading_signal(current_data, df.iloc[:i+1])
            
            # Execute trade
            self.execute_trade(signal, current_data, date)
            
            # Record equity curve
            if self.position:
                current_value = self.position_size * current_data['close']
            else:
                current_value = self.current_balance
                
            self.equity_curve.append({
                'date': date,
                'equity': current_value,
                'ticker': ticker
            })

    def run_backtest(self, ticker=None):
        """
        Run complete backtest
        
        Args:
            ticker (str): Single ticker to test, or None to test all
        """
        print(f"Starting backtest with initial balance: ${self.initial_balance}")
        print(f"Risk per trade: {self.risk_per_trade*100}%")
        print(f"Date range: {self.start_date} to {self.end_date}")
        
        if ticker:
            tickers_to_test = [ticker]
        else:
            tickers_to_test = self.tickers
            
        for ticker in tickers_to_test:
            try:
                self.backtest_single_ticker(ticker)
            except Exception as e:
                print(f"Error backtesting {ticker}: {e}")
                continue

    def calculate_performance_metrics(self):
        """Calculate comprehensive performance metrics"""
        if not self.trades:
            print("No trades executed during backtest period")
            return {}
            
        # Trade analysis
        profitable_trades = [t for t in self.trades if t.get('pnl', 0) > 0]
        losing_trades = [t for t in self.trades if t.get('pnl', 0) < 0]
        
        total_trades = len([t for t in self.trades if 'pnl' in t])
        win_rate = len(profitable_trades) / total_trades if total_trades > 0 else 0
        
        # P&L analysis
        total_pnl = sum(t.get('pnl', 0) for t in self.trades)
        total_return = (self.current_balance - self.initial_balance) / self.initial_balance * 100
        
        # Average trade metrics
        avg_win = np.mean([t['pnl'] for t in profitable_trades]) if profitable_trades else 0
        avg_loss = np.mean([t['pnl'] for t in losing_trades]) if losing_trades else 0
        
        # Risk metrics
        if len(self.equity_curve) > 1:
            equity_df = pd.DataFrame(self.equity_curve)
            equity_df['returns'] = equity_df['equity'].pct_change()
            
            max_drawdown = self.calculate_max_drawdown(equity_df['equity'])
            sharpe_ratio = self.calculate_sharpe_ratio(equity_df['returns'])
        else:
            max_drawdown = 0
            sharpe_ratio = 0
            
        metrics = {
            'total_trades': total_trades,
            'profitable_trades': len(profitable_trades),
            'losing_trades': len(losing_trades),
            'win_rate': win_rate * 100,
            'total_pnl': total_pnl,
            'total_return': total_return,
            'final_balance': self.current_balance,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio
        }
        
        return metrics

    def calculate_max_drawdown(self, equity_series):
        """Calculate maximum drawdown"""
        peak = equity_series.cummax()
        drawdown = (equity_series - peak) / peak * 100
        return abs(drawdown.min())

    def calculate_sharpe_ratio(self, returns_series, risk_free_rate=0.02):
        """Calculate Sharpe ratio"""
        if len(returns_series) < 2:
            return 0
            
        excess_returns = returns_series.mean() * 252 - risk_free_rate  # Annualized
        volatility = returns_series.std() * np.sqrt(252)  # Annualized
        
        return excess_returns / volatility if volatility > 0 else 0

    def plot_results(self, save_path=None):
        """Plot backtest results"""
        if not self.equity_curve:
            print("No equity curve data to plot")
            return
            
        # Create subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # Equity curve
        equity_df = pd.DataFrame(self.equity_curve)
        equity_df['date'] = pd.to_datetime(equity_df['date'])
        ax1.plot(equity_df['date'], equity_df['equity'])
        ax1.set_title('Equity Curve')
        ax1.set_ylabel('Portfolio Value ($)')
        ax1.grid(True)
        
        # Drawdown
        equity_df['peak'] = equity_df['equity'].cummax()
        equity_df['drawdown'] = (equity_df['equity'] - equity_df['peak']) / equity_df['peak'] * 100
        ax2.fill_between(equity_df['date'], equity_df['drawdown'], 0, color='red', alpha=0.3)
        ax2.set_title('Drawdown')
        ax2.set_ylabel('Drawdown (%)')
        ax2.grid(True)
        
        # Monthly returns
        if len(equity_df) > 1:
            equity_df.set_index('date', inplace=True)
            monthly_returns = equity_df['equity'].resample('M').last().pct_change() * 100
            monthly_returns.plot(kind='bar', ax=ax3)
        ax3.set_title('Monthly Returns')
        ax3.set_ylabel('Return (%)')
        ax3.grid(True)
        
        # Trade distribution
        trade_pnls = [t.get('pnl', 0) for t in self.trades if 'pnl' in t]
        if trade_pnls:
            ax4.hist(trade_pnls, bins=20, alpha=0.7)
        ax4.set_title('Trade P&L Distribution')
        ax4.set_xlabel('P&L ($)')
        ax4.set_ylabel('Frequency')
        ax4.grid(True)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Backtest results saved to: {save_path}")
        else:
            plt.show()
        
        plt.close()

    def save_results(self, filename="backtest_results.json"):
        """Save backtest results to file"""
        results = {
            'parameters': {
                'initial_balance': self.initial_balance,
                'risk_per_trade': self.risk_per_trade,
                'start_date': str(self.start_date),
                'end_date': str(self.end_date)
            },
            'performance_metrics': self.calculate_performance_metrics(),
            'trades': self.trades,
            'equity_curve': self.equity_curve
        }
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"Results saved to: {filename}")

    def print_summary(self):
        """Print backtest summary"""
        metrics = self.calculate_performance_metrics()
        
        print("\n" + "="*50)
        print("BACKTEST SUMMARY")
        print("="*50)
        print(f"Initial Balance:     ${self.initial_balance:,.2f}")
        print(f"Final Balance:       ${metrics.get('final_balance', 0):,.2f}")
        print(f"Total Return:        {metrics.get('total_return', 0):.2f}%")
        print(f"Total P&L:           ${metrics.get('total_pnl', 0):,.2f}")
        print()
        print(f"Total Trades:        {metrics.get('total_trades', 0)}")
        print(f"Profitable Trades:   {metrics.get('profitable_trades', 0)}")
        print(f"Losing Trades:       {metrics.get('losing_trades', 0)}")
        print(f"Win Rate:            {metrics.get('win_rate', 0):.2f}%")
        print()
        print(f"Average Win:         ${metrics.get('avg_win', 0):.2f}")
        print(f"Average Loss:        ${metrics.get('avg_loss', 0):.2f}")
        print(f"Max Drawdown:        {metrics.get('max_drawdown', 0):.2f}%")
        print(f"Sharpe Ratio:        {metrics.get('sharpe_ratio', 0):.2f}")
        print("="*50)


def run_comprehensive_backtest():
    """Run a comprehensive backtest with multiple scenarios"""
    print("Starting Comprehensive Backtest Analysis...")
    
    # Test different parameters
    scenarios = [
        {"initial_balance": 1000, "risk_per_trade": 0.01, "name": "Conservative"},
        {"initial_balance": 1000, "risk_per_trade": 0.02, "name": "Moderate"},
        {"initial_balance": 1000, "risk_per_trade": 0.05, "name": "Aggressive"}
    ]
    
    # Date range for testing (last 6 months)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    
    results = {}
    
    for scenario in scenarios:
        print(f"\n--- Testing {scenario['name']} Strategy ---")
        
        # Create backtest engine
        engine = BacktestEngine(
            initial_balance=scenario['initial_balance'],
            risk_per_trade=scenario['risk_per_trade'],
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d')
        )
        
        # Run backtest
        engine.run_backtest()
        
        # Get results
        metrics = engine.calculate_performance_metrics()
        results[scenario['name']] = metrics
        
        # Print summary
        engine.print_summary()
        
        # Save individual results
        engine.save_results(f"backtest_{scenario['name'].lower()}.json")
        
        # Plot results
        engine.plot_results(f"backtest_{scenario['name'].lower()}_chart.png")
    
    # Compare scenarios
    print("\n" + "="*80)
    print("SCENARIO COMPARISON")
    print("="*80)
    print(f"{'Scenario':<15} {'Return %':<10} {'Win Rate %':<12} {'Max DD %':<10} {'Sharpe':<8}")
    print("-"*80)
    
    for name, metrics in results.items():
        print(f"{name:<15} {metrics.get('total_return', 0):<10.2f} "
              f"{metrics.get('win_rate', 0):<12.2f} {metrics.get('max_drawdown', 0):<10.2f} "
              f"{metrics.get('sharpe_ratio', 0):<8.2f}")
    
    return results

def backtest_strategy(initial_balance=1000, risk_per_trade=0.02, start_date=None, end_date=None, ticker=None):
    """
    Simple interface function for backtesting a trading strategy
    This is the function name you were looking for!
    
    Args:
        initial_balance (float): Starting account balance
        risk_per_trade (float): Risk percentage per trade
        start_date (str): Start date for backtesting (YYYY-MM-DD) 
        end_date (str): End date for backtesting (YYYY-MM-DD)
        ticker (str): Single ticker to test, or None for all tickers
        
    Returns:
        dict: Backtest results and performance metrics
    """
    print("=== Starting backtest_strategy function ===")
    
    # Create backtest engine
    engine = BacktestEngine(
        initial_balance=initial_balance,
        risk_per_trade=risk_per_trade, 
        start_date=start_date,
        end_date=end_date
    )
    
    # Run the backtest
    engine.run_backtest(ticker)
    
    # Get performance metrics
    results = engine.calculate_performance_metrics()
    
    # Print summary
    engine.print_summary()
    
    return results

def backtesting_loop(tickers=None, scenarios=None):
    """
    Loop through multiple backtesting scenarios and tickers
    This is the second function name you were looking for!
    
    Args:
        tickers (list): List of tickers to test
        scenarios (list): List of parameter scenarios to test
        
    Returns:
        dict: Results for all scenarios and tickers
    """
    print("=== Starting backtesting_loop function ===")
    
    if tickers is None:
        tickers = ["PETR4", "VALE3", "ITUB4", "AMER3", "B3SA3"]
        
    if scenarios is None:
        scenarios = [
            {"initial_balance": 1000, "risk_per_trade": 0.01, "name": "Conservative"},
            {"initial_balance": 1000, "risk_per_trade": 0.02, "name": "Moderate"},
            {"initial_balance": 1000, "risk_per_trade": 0.05, "name": "Aggressive"}
        ]
    
    all_results = {}
    
    # Date range for testing (last 6 months)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    
    for scenario in scenarios:
        print(f"\n--- Testing {scenario['name']} Strategy ---")
        scenario_results = {}
        
        for ticker in tickers:
            print(f"\nBacktesting {ticker} with {scenario['name']} parameters...")
            
            try:
                # Run backtest for this ticker and scenario
                results = backtest_strategy(
                    initial_balance=scenario['initial_balance'],
                    risk_per_trade=scenario['risk_per_trade'],
                    start_date=start_date.strftime('%Y-%m-%d'),
                    end_date=end_date.strftime('%Y-%m-%d'),
                    ticker=ticker
                )
                scenario_results[ticker] = results
                
            except Exception as e:
                print(f"Error backtesting {ticker}: {e}")
                scenario_results[ticker] = {"error": str(e)}
        
        all_results[scenario['name']] = scenario_results
    
    # Print comparison summary
    print("\n" + "="*100)
    print("BACKTESTING LOOP SUMMARY")
    print("="*100)
    print(f"{'Scenario':<12} {'Ticker':<8} {'Return %':<10} {'Win Rate %':<12} {'Trades':<8} {'Sharpe':<8}")
    print("-"*100)
    
    for scenario_name, scenario_data in all_results.items():
        for ticker, results in scenario_data.items():
            if "error" not in results:
                print(f"{scenario_name:<12} {ticker:<8} {results.get('total_return', 0):<10.2f} "
                      f"{results.get('win_rate', 0):<12.2f} {results.get('total_trades', 0):<8} "
                      f"{results.get('sharpe_ratio', 0):<8.2f}")
            else:
                print(f"{scenario_name:<12} {ticker:<8} ERROR: {results['error']}")
    
    return all_results


if __name__ == "__main__":
    # Run comprehensive backtest
    results = run_comprehensive_backtest()
