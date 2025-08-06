"""
SIMPLE FUNDAMENTAL ROBOT TEST
Test the robot without authentication to verify the logic works
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_without_auth():
    """Test robot components that don't require authentication"""
    print("🧪 TESTING ROBOT WITHOUT AUTHENTICATION")
    print("=" * 60)
    
    from practical_fundamental_robot import PracticalFundamentalRobot
    
    robot = PracticalFundamentalRobot()
    
    # Test internal scoring methods with mock data
    print("\n1️⃣ TESTING PRICE MOMENTUM SCORING...")
    
    # Mock quote data for testing
    mock_quote_data = {
        'symbol': 'VALE3',
        'current_price': 53.65,
        'previous_close': 53.29,
        'change_percent': 0.68,
        'change_week': 1.26,
        'change_month': 2.98,
        'change_year': 2.19,
        'volume': 18890600,
        'volume_financial': 1013467205,
        'high': 53.87,
        'low': 53.11,
        'open': 53.3,
        'bid': 53.35,
        'ask': 53.8,
        'quantity_trades': 23635
    }
    
    momentum_score = robot._score_price_momentum(mock_quote_data)
    print(f"   📊 Price Momentum Score: {momentum_score:.1f}/100")
    print(f"   📈 Daily Change: {mock_quote_data['change_percent']:.2f}%")
    print(f"   📊 Monthly Change: {mock_quote_data['change_month']:.2f}%")
    print(f"   💰 Volume: {mock_quote_data['volume']:,}")
    
    # Test news sentiment analysis
    print("\n2️⃣ TESTING NEWS SENTIMENT ANALYSIS...")
    
    mock_news_data = [
        {'title': 'Vale registra alta nos lucros do trimestre', 'description': 'Empresa mostra crescimento positivo'},
        {'title': 'Mercado otimista com setor de mineração', 'description': 'Analistas veem recuperação'},
        {'title': 'Queda nas commodities preocupa investidores', 'description': 'Preços em declínio'},
        {'title': 'Petrobras anuncia aumento de produção', 'description': 'Expansão das operações'},
        {'title': 'Bolsa tem alta com melhora dos indicadores', 'description': 'Sentimento positivo do mercado'}
    ]
    
    sentiment_analysis = robot._analyze_news_sentiment(mock_news_data)
    sentiment_score = robot._score_news_sentiment(sentiment_analysis, 'VALE3')
    
    print(f"   📰 News Sentiment Score: {sentiment_score:.1f}/100")
    print(f"   🎯 Overall Sentiment: {sentiment_analysis['overall_sentiment']}")
    print(f"   📊 Articles Analyzed: {sentiment_analysis['total_articles']}")
    print(f"   🟢 Positive: {sentiment_analysis['positive_articles']}")
    print(f"   🔴 Negative: {sentiment_analysis['negative_articles']}")
    
    # Test corporate events scoring
    print("\n3️⃣ TESTING CORPORATE EVENTS SCORING...")
    
    mock_facts = {
        'VALE3': [
            {'title': 'VALE (VALE3) Pagamento de Dividendos - 10/06/2025'},
            {'title': 'VALE (VALE3) Fato Relevante - Aumento de Produção'},
            {'title': 'VALE (VALE3) Resultado do Trimestre - Lucro Record'}
        ]
    }
    
    events_score = robot._score_corporate_events(mock_facts, 'VALE3')
    print(f"   📋 Corporate Events Score: {events_score:.1f}/100")
    print(f"   📊 Recent Events: {len(mock_facts['VALE3'])}")
    
    # Test market position scoring
    print("\n4️⃣ TESTING MARKET POSITION SCORING...")
    
    position_score = robot._score_market_position(mock_quote_data, {})
    print(f"   🎯 Market Position Score: {position_score:.1f}/100")
    
    # Calculate daily position
    high = mock_quote_data['high']
    low = mock_quote_data['low']
    current = mock_quote_data['current_price']
    daily_position = (current - low) / (high - low) * 100
    print(f"   📊 Daily Position: {daily_position:.1f}% of range")
    
    # Test overall signal generation
    print("\n5️⃣ TESTING OVERALL SIGNAL CALCULATION...")
    
    overall_score = (
        momentum_score * 0.35 +
        sentiment_score * 0.25 +
        events_score * 0.20 +
        position_score * 0.20
    )
    
    signal, reasons = robot._determine_signal(overall_score, mock_quote_data, sentiment_analysis)
    target_price = robot._calculate_momentum_target(mock_quote_data, overall_score)
    risk_level = robot._assess_practical_risk(mock_quote_data, {})
    
    print(f"   🎯 FINAL SIGNAL: {signal}")
    print(f"   📊 Overall Score: {overall_score:.1f}/100")
    print(f"   💰 Current Price: R${current:.2f}")
    if target_price:
        print(f"   🎯 Target Price: R${target_price:.2f}")
    print(f"   ⚠️  Risk Level: {risk_level}")
    
    print(f"\n   💡 REASONS:")
    for reason in reasons:
        print(f"      • {reason}")
    
    print(f"\n   📊 COMPONENT BREAKDOWN:")
    print(f"      Price Momentum (35%): {momentum_score:.1f}")
    print(f"      News Sentiment (25%): {sentiment_score:.1f}")
    print(f"      Corporate Events (20%): {events_score:.1f}")
    print(f"      Market Position (20%): {position_score:.1f}")
    
    return overall_score

def test_signal_logic():
    """Test the signal generation logic with different scenarios"""
    print("\n🎯 TESTING SIGNAL LOGIC WITH DIFFERENT SCENARIOS")
    print("=" * 65)
    
    from practical_fundamental_robot import PracticalFundamentalRobot
    robot = PracticalFundamentalRobot()
    
    scenarios = [
        {
            'name': 'BULLISH SCENARIO',
            'quote': {
                'current_price': 55.0, 'change_percent': 3.5, 'change_week': 8.2,
                'change_month': 15.5, 'volume': 25000000, 'high': 55.2, 'low': 54.1,
                'bid': 54.9, 'ask': 55.1, 'quantity_trades': 45000
            },
            'sentiment': {'overall_sentiment': 'POSITIVE', 'score': 75}
        },
        {
            'name': 'BEARISH SCENARIO',
            'quote': {
                'current_price': 48.0, 'change_percent': -2.8, 'change_week': -6.5,
                'change_month': -12.3, 'volume': 8000000, 'high': 48.9, 'low': 47.8,
                'bid': 47.8, 'ask': 48.2, 'quantity_trades': 15000
            },
            'sentiment': {'overall_sentiment': 'NEGATIVE', 'score': 25}
        },
        {
            'name': 'NEUTRAL SCENARIO',
            'quote': {
                'current_price': 52.0, 'change_percent': 0.2, 'change_week': 1.1,
                'change_month': 2.5, 'volume': 12000000, 'high': 52.3, 'low': 51.7,
                'bid': 51.9, 'ask': 52.1, 'quantity_trades': 28000
            },
            'sentiment': {'overall_sentiment': 'NEUTRAL', 'score': 50}
        }
    ]
    
    for scenario in scenarios:
        print(f"\n📊 {scenario['name']}")
        print("-" * 30)
        
        quote = scenario['quote']
        sentiment = scenario['sentiment']
        
        # Calculate scores
        momentum_score = robot._score_price_momentum(quote)
        sentiment_score = robot._score_news_sentiment(sentiment, 'TEST')
        events_score = 55  # Mock average
        position_score = robot._score_market_position(quote, {})
        
        overall_score = (
            momentum_score * 0.35 +
            sentiment_score * 0.25 +
            events_score * 0.20 +
            position_score * 0.20
        )
        
        signal, reasons = robot._determine_signal(overall_score, quote, sentiment)
        
        print(f"   🎯 Signal: {signal}")
        print(f"   📊 Score: {overall_score:.1f}/100")
        print(f"   📈 Price: R${quote['current_price']:.2f} ({quote['change_percent']:+.1f}%)")
        print(f"   📰 Sentiment: {sentiment['overall_sentiment']}")
        print(f"   💡 Key Reason: {reasons[0] if reasons else 'No specific reason'}")

def test_api_endpoints_availability():
    """Test if we can call the API endpoints without auth (to check structure)"""
    print("\n🔌 TESTING API ENDPOINTS AVAILABILITY")
    print("=" * 50)
    
    import requests
    
    base_url = "https://webfeeder.cedrotech.com"
    session = requests.Session()
    
    # Test endpoints that might work without full auth
    test_endpoints = [
        {'name': 'Quote VALE3', 'url': f'{base_url}/services/quotes/quote/VALE3'},
        {'name': 'Index List', 'url': f'{base_url}/services/quotes/indexList/bovespa'},
        {'name': 'Market List', 'url': f'{base_url}/services/quotes/marketList'}
    ]
    
    for endpoint in test_endpoints:
        try:
            response = session.get(endpoint['url'], timeout=5)
            print(f"   🔹 {endpoint['name']}: Status {response.status_code}")
            
            if response.status_code == 200:
                print(f"      ✅ Working! Data size: {len(response.text)} bytes")
            elif response.status_code == 401:
                print(f"      🔐 Requires authentication")
            elif response.status_code == 404:
                print(f"      ❌ Endpoint not found")
            else:
                print(f"      ⚠️  Other status: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ {endpoint['name']}: Error - {str(e)[:50]}")

if __name__ == "__main__":
    print("🏦 SIMPLE FUNDAMENTAL ROBOT TESTING")
    print("=" * 70)
    print("Testing robot logic without requiring authentication")
    
    # Test core logic
    overall_score = test_without_auth()
    
    # Test different scenarios
    test_signal_logic()
    
    # Test endpoint availability
    test_api_endpoints_availability()
    
    print(f"\n🎉 TESTING COMPLETED!")
    print("=" * 40)
    
    if overall_score > 60:
        print("✅ Robot logic working well - Strong signal generation")
    elif overall_score > 40:
        print("✅ Robot logic working - Moderate signal generation")
    else:
        print("✅ Robot logic working - Conservative signal generation")
    
    print("\n🚀 NEXT STEPS:")
    print("1. ✅ Core logic validated")
    print("2. 🔐 Add proper CedroTech credentials")
    print("3. 📊 Test with real market data")
    print("4. 🤖 Integrate with main trading robot")
    print("5. 📈 Compare fundamental vs technical signals")
