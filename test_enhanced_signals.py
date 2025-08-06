"""
Test the robot's signal generation with the fixed logic
This will help us understand why the robot hasn't been trading
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.quick_technical_analysis import get_price_signals
from utils.database import fetch_intraday_prices

def test_robot_signal_generation():
    """Test signal generation for EMBR3 (the current selected asset)."""
    
    print("🔍 TESTING ROBOT SIGNAL GENERATION")
    print("=" * 60)
    
    # Test with EMBR3 (current holding_asset from robot_state.json)
    ticker = "EMBR3"
    print(f"📊 Testing signals for {ticker}...")
    
    # Fetch real intraday prices from database
    intraday_prices = fetch_intraday_prices(ticker)
    
    if not intraday_prices:
        print(f"❌ No intraday prices found for {ticker}")
        print("📋 Available alternatives:")
        
        # Try other common tickers
        test_tickers = ["VALE3", "PETR4", "ITUB4", "BBAS3"]
        for test_ticker in test_tickers:
            test_prices = fetch_intraday_prices(test_ticker)
            if test_prices:
                print(f"   ✅ {test_ticker}: {len(test_prices)} price records available")
                ticker = test_ticker
                intraday_prices = test_prices
                break
            else:
                print(f"   ❌ {test_ticker}: No data")
    
    if not intraday_prices:
        print("\n❌ No intraday data available for any ticker!")
        print("🔧 Solution: Run data fetching first:")
        print("   python -c \"from utils.quick_technical_analysis import fetch_and_store_intraday_for_all; fetch_and_store_intraday_for_all(['EMBR3', 'VALE3', 'PETR4'])\"")
        return
    
    print(f"\n📈 Found {len(intraday_prices)} price records for {ticker}")
    print(f"📊 Latest prices (last 5 records):")
    
    # Show recent price data
    for i, price in enumerate(intraday_prices[-5:]):
        print(f"   {i+1}. Close: R${price['close']:.2f}, High: R${price['high']:.2f}, Low: R${price['low']:.2f}, Volume: {price.get('volume', 0):,}")
    
    # Test signal generation
    print(f"\n🎯 TESTING ENHANCED SIGNALS...")
    signal, high, low = get_price_signals(intraday_prices)
    
    print(f"\n🚀 SIGNAL RESULTS:")
    print(f"   Signal: {signal}")
    print(f"   Recent High: R${high:.2f}")
    print(f"   Recent Low: R${low:.2f}")
    
    if signal == 'buy':
        print(f"\n✅ SUCCESS! Robot should execute BUY trade for {ticker}")
        print("🎯 This fixes the issue where robot was stuck in 'hold' mode")
    elif signal == 'sell':
        print(f"\n⚠️ SELL signal generated for {ticker}")
        print("📊 This is normal - robot will wait for better entry")
    else:
        print(f"\n⚠️ Still getting HOLD signal for {ticker}")
        print("📋 This might indicate:")
        print("   - Insufficient price movement")
        print("   - Need more historical data")
        print("   - Market conditions not favorable")
    
    return signal, ticker

def test_multiple_assets():
    """Test signal generation for multiple assets to see which ones would trade."""
    
    print("\n" + "=" * 60)
    print("🔍 TESTING MULTIPLE ASSETS FOR TRADING OPPORTUNITIES")
    print("=" * 60)
    
    # List of tickers from robot
    tickers = [
        "PETR4", "VALE3", "ITUB4", "AMER3", "B3SA3", "MGLU3", "LREN3", 
        "ITSA4", "BBAS3", "RENT3", "ABEV3", "SUZB3", "WEG3", "BRFS3", 
        "BBDC4", "CRFB3", "BPAC11", "GGBR3", "EMBR3", "CMIN3"
    ]
    
    buy_candidates = []
    sell_candidates = []
    hold_candidates = []
    
    for ticker in tickers[:10]:  # Test first 10 to avoid too much output
        try:
            intraday_prices = fetch_intraday_prices(ticker)
            if intraday_prices:
                signal, high, low = get_price_signals(intraday_prices)
                current_price = intraday_prices[0]['close'] if intraday_prices else 0
                
                if signal == 'buy':
                    buy_candidates.append((ticker, current_price, high, low))
                elif signal == 'sell':
                    sell_candidates.append((ticker, current_price, high, low))
                else:
                    hold_candidates.append((ticker, current_price, high, low))
                    
                print(f"📊 {ticker}: {signal.upper()} @ R${current_price:.2f}")
            else:
                print(f"❌ {ticker}: No data")
        except Exception as e:
            print(f"❌ {ticker}: Error - {str(e)[:50]}")
    
    print(f"\n🎯 SUMMARY:")
    print(f"   🚀 BUY signals: {len(buy_candidates)}")
    print(f"   💰 SELL signals: {len(sell_candidates)}")
    print(f"   ⏸️ HOLD signals: {len(hold_candidates)}")
    
    if buy_candidates:
        print(f"\n✅ TRADING OPPORTUNITIES FOUND:")
        for ticker, price, high, low in buy_candidates:
            print(f"   🚀 {ticker}: BUY @ R${price:.2f} (Range: R${low:.2f}-R${high:.2f})")
    else:
        print(f"\n⚠️ No BUY signals generated")
        print("📋 This could mean:")
        print("   - Market conditions not favorable")
        print("   - Need fresh intraday data")
        print("   - Signal parameters need adjustment")

if __name__ == "__main__":
    # Test signal generation
    signal, ticker = test_robot_signal_generation()
    
    # Test multiple assets
    test_multiple_assets()
    
    print(f"\n🔧 NEXT STEPS:")
    if signal == 'buy':
        print("✅ Enhanced signals are working - robot should start trading!")
        print(f"📤 Run the robot and it should buy {ticker}")
    else:
        print("⚠️ May need to fetch fresh intraday data or adjust parameters")
        print("📊 Try running: python utils/quick_technical_analysis.py")
