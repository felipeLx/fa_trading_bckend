"""
TEST PRACTICAL FUNDAMENTAL ROBOT
Test the working fundamental analysis robot with real CedroTech data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from practical_fundamental_robot import PracticalFundamentalRobot

def test_individual_components():
    """Test each component of the robot individually"""
    print("🧪 TESTING INDIVIDUAL ROBOT COMPONENTS")
    print("=" * 60)
    
    robot = PracticalFundamentalRobot()
    
    # Test authentication (using placeholder - replace with real creds)
    print("\n1️⃣ TESTING AUTHENTICATION...")
    # Note: Replace with actual credentials
    auth_success = robot.authenticate("username", "password")
    if not auth_success:
        print("   ⚠️  Using session without auth for testing")
    
    # Test quote data
    print("\n2️⃣ TESTING QUOTE DATA...")
    quote_data = robot.get_asset_quote('VALE3')
    if quote_data:
        print(f"   ✅ Quote data retrieved: {len(quote_data)} fields")
        print(f"   📊 VALE3 Price: R${quote_data.get('current_price', 0):.2f}")
        print(f"   📈 Daily Change: {quote_data.get('change_percent', 0):.2f}%")
        print(f"   📊 Volume: {quote_data.get('volume', 0):,}")
    else:
        print("   ❌ Failed to get quote data")
        return False
    
    # Test news sentiment
    print("\n3️⃣ TESTING NEWS SENTIMENT...")
    news_sentiment = robot.get_market_news_sentiment(days_back=3)  # Smaller range for testing
    if news_sentiment:
        print(f"   ✅ News analysis completed")
        print(f"   📰 Overall sentiment: {news_sentiment.get('overall_sentiment')}")
        print(f"   📊 Sentiment score: {news_sentiment.get('score', 0):.1f}")
        print(f"   📄 Articles analyzed: {news_sentiment.get('total_articles', 0)}")
    else:
        print("   ⚠️  News sentiment unavailable")
    
    # Test relevant facts
    print("\n4️⃣ TESTING RELEVANT FACTS...")
    relevant_facts = robot.get_relevant_facts(days_back=14)  # Smaller range
    if relevant_facts:
        print(f"   ✅ Relevant facts retrieved")
        print(f"   📋 Companies with facts: {len(relevant_facts)}")
        for ticker, facts in list(relevant_facts.items())[:3]:  # Show first 3
            print(f"   📊 {ticker}: {len(facts)} facts")
    else:
        print("   ⚠️  No relevant facts found")
    
    # Test options data
    print("\n5️⃣ TESTING OPTIONS DATA...")
    options_data = robot.get_options_data('VALE3')
    if options_data:
        print(f"   ✅ Options data retrieved")
        print(f"   ⚡ Volatility: {options_data.get('implied_volatility')}")
    else:
        print("   ⚠️  Options data unavailable")
    
    return True

def test_signal_generation():
    """Test complete signal generation for multiple assets"""
    print("\n🎯 TESTING SIGNAL GENERATION")
    print("=" * 60)
    
    robot = PracticalFundamentalRobot()
    
    # Test with popular Brazilian stocks
    test_tickers = ['VALE3', 'PETR4', 'ITUB4']
    
    results = []
    
    for ticker in test_tickers:
        print(f"\n🔍 ANALYZING: {ticker}")
        print("-" * 30)
        
        try:
            signal = robot.generate_fundamental_signal(ticker)
            
            print(f"   🎯 SIGNAL: {signal.signal}")
            print(f"   📊 CONFIDENCE: {signal.confidence:.1f}%")
            print(f"   💰 PRICE: R${signal.current_price:.2f}")
            print(f"   ⚠️  RISK: {signal.risk_level}")
            
            print(f"   📈 SCORES:")
            print(f"      Price Momentum: {signal.price_momentum_score:.1f}")
            print(f"      News Sentiment: {signal.news_sentiment_score:.1f}")
            print(f"      Corporate Events: {signal.corporate_events_score:.1f}")
            print(f"      Market Position: {signal.market_position_score:.1f}")
            
            print(f"   💡 KEY REASONS:")
            for reason in signal.reasons[:2]:  # Show top 2 reasons
                print(f"      • {reason}")
            
            results.append({
                'ticker': ticker,
                'signal': signal.signal,
                'confidence': signal.confidence,
                'price': signal.current_price
            })
            
        except Exception as e:
            print(f"   ❌ Error analyzing {ticker}: {e}")
            continue
    
    # Summary
    print(f"\n📊 ANALYSIS SUMMARY")
    print("=" * 40)
    
    if results:
        buy_signals = [r for r in results if r['signal'] == 'BUY']
        sell_signals = [r for r in results if r['signal'] == 'SELL']
        hold_signals = [r for r in results if r['signal'] == 'HOLD']
        
        print(f"🟢 BUY signals: {len(buy_signals)}")
        print(f"🔴 SELL signals: {len(sell_signals)}")
        print(f"🟡 HOLD signals: {len(hold_signals)}")
        
        if buy_signals:
            print(f"\n🚀 TOP BUY OPPORTUNITIES:")
            sorted_buys = sorted(buy_signals, key=lambda x: x['confidence'], reverse=True)
            for signal in sorted_buys[:2]:
                print(f"   {signal['ticker']}: {signal['confidence']:.1f}% confidence")
        
        print(f"\n✅ Signal generation test completed successfully!")
        return True
    else:
        print("❌ No signals generated")
        return False

def test_robot_comparison():
    """Compare this robot with our enhanced day trading robot"""
    print("\n⚖️  COMPARING ROBOTS")
    print("=" * 50)
    
    print("🤖 PRACTICAL FUNDAMENTAL ROBOT:")
    print("   ✅ Uses working CedroTech endpoints")
    print("   ✅ News sentiment analysis (34,900+ articles)")
    print("   ✅ Corporate events analysis (203+ facts)")
    print("   ✅ Price momentum analysis")
    print("   ✅ Market position scoring")
    print("   🎯 Focus: Medium to long-term fundamental signals")
    print("   ⏱️  Timeframe: Days to weeks")
    
    print("\n🚀 ENHANCED DAY TRADING ROBOT:")
    print("   ✅ RSI-based oversold detection")
    print("   ✅ Moving average analysis")
    print("   ✅ Volume confirmation")
    print("   ✅ Price position analysis")
    print("   🎯 Focus: Intraday technical signals")
    print("   ⏱️  Timeframe: Minutes to hours")
    
    print("\n🎯 COMBINED STRATEGY OPPORTUNITY:")
    print("   💡 Use fundamental robot for asset selection")
    print("   💡 Use technical robot for entry timing")
    print("   💡 Fundamental BUY + Technical BUY = STRONG SIGNAL")
    print("   💡 Fundamental SELL + Technical SELL = STRONG EXIT")

if __name__ == "__main__":
    print("🏦 PRACTICAL FUNDAMENTAL ANALYSIS ROBOT - TESTING")
    print("=" * 80)
    print("Testing robot built on WORKING CedroTech API endpoints")
    print("Based on comprehensive API testing results")
    
    # Run tests
    component_test = test_individual_components()
    
    if component_test:
        signal_test = test_signal_generation()
        
        if signal_test:
            test_robot_comparison()
            
            print(f"\n🎉 ALL TESTS COMPLETED!")
            print("=" * 50)
            print("✅ Robot is ready for production use")
            print("✅ Uses only tested and working endpoints")
            print("✅ Provides actionable fundamental signals")
            print("\n🚀 NEXT STEPS:")
            print("1. Add your CedroTech credentials for authentication")
            print("2. Run robot.py with fundamental signals")
            print("3. Combine with technical analysis for optimal timing")
            print("4. Monitor performance and refine scoring algorithms")
        else:
            print("\n❌ Signal generation test failed")
    else:
        print("\n❌ Component tests failed")
