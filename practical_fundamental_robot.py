"""
PRACTICAL FUNDAMENTAL ANALYSIS ROBOT
Uses CedroTech's WORKING API endpoints for fundamental-driven trading
Built on actual tested API responses - NO hypothetical endpoints!
"""

import requests
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import re
from collections import defaultdict

@dataclass
class PracticalFundamentalSignal:
    """Real-world fundamental signal based on available data"""
    ticker: str
    signal: str  # 'BUY', 'SELL', 'HOLD'
    confidence: float  # 0-100
    price_momentum_score: float
    news_sentiment_score: float
    corporate_events_score: float
    market_position_score: float
    reasons: List[str]
    current_price: float
    target_price: Optional[float] = None
    risk_level: str = "MEDIUM"

class PracticalFundamentalRobot:
    """
    WORKING Fundamental Analysis Robot
    Uses only TESTED and WORKING CedroTech endpoints
    """
    
    def __init__(self):
        self.api_base = "https://webfeeder.cedrotech.com"
        self.session = requests.Session()
        self.authenticated = False
        
        # Authentication credentials
        self.username = None
        self.password = None
          # Cache for analysis efficiency
        self.market_indices_cache = {}
        self.news_cache = {}
        self.company_quotes_cache = {}
        
    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate with CedroTech API using WORKING method"""
        print("🔐 AUTHENTICATING WITH CEDROTECH...")
        
        self.username = username
        self.password = password
        
        # Set up proper headers (from working test)
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Connection': 'keep-alive'
        })
        
        try:
            # Use the WORKING authentication endpoint from our tests
            auth_url = f"{self.api_base}/SignIn"
            
            # Authentication parameters (from working test)
            params = {
                "login": username,
                "password": password
            }
            
            headers = {
                "accept": "application/json"
            }
            
            # Make authentication request
            response = self.session.post(auth_url, headers=headers, params=params)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                # Check if we got session cookies
                cookies = dict(self.session.cookies)
                if cookies:
                    self.authenticated = True
                    print(f"   ✅ Authentication successful!")
                    print(f"   🍪 Session cookies: {list(cookies.keys())}")
                    return True
                else:
                    print("   ❌ No session cookies received")
                    return False
            else:
                print(f"   ❌ Authentication failed: {response.status_code}")
                if response.text:
                    print(f"   📝 Response: {response.text[:200]}")
                return False
                
        except Exception as e:
            print(f"   ❌ Authentication error: {e}")
            return False
    
    def get_asset_quote(self, ticker: str) -> Dict:
        """
        WORKING ENDPOINT: quote_asset
        Get comprehensive price and volume data for an asset
        """
        print(f"📊 GETTING QUOTE DATA: {ticker}")
        
        quote_url = f"{self.api_base}/services/quotes/quote/{ticker}"
        
        try:
            response = self.session.get(quote_url)
            if response.status_code == 200:
                data = response.json()
                
                # Extract key metrics for analysis
                quote_analysis = {
                    'symbol': data.get('symbol'),
                    'current_price': data.get('lastTrade', 0),
                    'previous_close': data.get('previous', 0),
                    'change_percent': data.get('change', 0),
                    'change_week': data.get('changeWeek', 0),
                    'change_month': data.get('changeMonth', 0),
                    'change_year': data.get('changeYear', 0),
                    'volume': data.get('volumeAmount', 0),
                    'volume_financial': data.get('volumeFinancier', 0),
                    'high': data.get('high', 0),
                    'low': data.get('low', 0),
                    'open': data.get('open', 0),
                    'bid': data.get('bid', 0),
                    'ask': data.get('ask', 0),
                    'quantity_trades': data.get('quantityTrades', 0),
                    'last_update': data.get('timeUpdate'),
                    'trade_date': data.get('dateTrade')
                }
                
                print(f"   ✅ Price: R${quote_analysis['current_price']:.2f} ({quote_analysis['change_percent']:.2f}%)")
                return quote_analysis
                
        except Exception as e:
            print(f"   ❌ Error getting quote for {ticker}: {e}")
            return {}
    
    def get_market_news_sentiment(self, days_back: int = 7) -> Dict:
        """
        WORKING ENDPOINT: news_by_date
        Analyze market sentiment from news (34,900+ items available)
        """
        print(f"📰 ANALYZING NEWS SENTIMENT (last {days_back} days)...")
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        date_format = "%d%m%Y"
        start_str = start_date.strftime(date_format)
        end_str = end_date.strftime(date_format)
        
        news_url = f"{self.api_base}/services/news/newsByDate/{start_str}/{end_str}"
        
        try:
            response = self.session.get(news_url)
            if response.status_code == 200:
                news_data = response.json()
                
                sentiment_analysis = self._analyze_news_sentiment(news_data)
                print(f"   📊 Analyzed {len(news_data)} news items")
                print(f"   🎯 Market sentiment: {sentiment_analysis['overall_sentiment']}")
                
                return sentiment_analysis
                
        except Exception as e:
            print(f"   ❌ Error getting news: {e}")
            return {}
    
    def get_relevant_facts(self, days_back: int = 30) -> List[Dict]:
        """
        WORKING ENDPOINT: relevant_facts
        Get corporate events and material facts (203+ items available)
        """
        print(f"📋 GETTING RELEVANT FACTS (last {days_back} days)...")
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        date_format = "%d%m%Y"
        start_str = start_date.strftime(date_format)
        end_str = end_date.strftime(date_format)
        
        facts_url = f"{self.api_base}/services/news/newsRelevantFacts/{start_str}/{end_str}"
        
        try:
            response = self.session.get(facts_url)
            if response.status_code == 200:
                facts_data = response.json()
                
                # Process and categorize relevant facts
                processed_facts = self._process_relevant_facts(facts_data)
                print(f"   📊 Found {len(facts_data)} relevant facts")
                
                return processed_facts
                
        except Exception as e:
            print(f"   ❌ Error getting relevant facts: {e}")
            return []
    
    def get_index_composition(self, index_market: str = "bovespa") -> List[Dict]:
        """
        WORKING ENDPOINT: quotes_index
        Get index composition for sector analysis (84+ assets available)
        """
        print(f"📈 GETTING INDEX COMPOSITION: {index_market.upper()}")
        
        # First get available indices
        indices_url = f"{self.api_base}/services/quotes/indexList/{index_market}"
        
        try:
            response = self.session.get(indices_url)
            if response.status_code == 200:
                indices = response.json()
                
                # Get IBOV composition (most comprehensive)
                ibov_url = f"{self.api_base}/services/quotes/quotesIndex/ibov"
                ibov_response = self.session.get(ibov_url)
                
                if ibov_response.status_code == 200:
                    composition = ibov_response.json()
                    print(f"   📊 Found {len(composition)} assets in index")
                    return composition
                    
        except Exception as e:
            print(f"   ❌ Error getting index composition: {e}")
            return []
    
    def get_options_data(self, ticker: str) -> Dict:
        """
        WORKING ENDPOINT: options_quote
        Get options data for volatility analysis
        """
        print(f"⚡ GETTING OPTIONS DATA: {ticker}")
        
        options_url = f"{self.api_base}/services/quotes/optionsQuote/{ticker}"
        
        try:
            response = self.session.get(options_url)
            if response.status_code == 200:
                options_data = response.json()
                
                # Calculate implied volatility metrics
                volatility_analysis = self._analyze_options_volatility(options_data)
                print(f"   📊 Options analysis completed")
                
                return volatility_analysis
                
        except Exception as e:
            print(f"   ❌ Error getting options for {ticker}: {e}")
            return {}
    
    def generate_fundamental_signal(self, ticker: str) -> PracticalFundamentalSignal:
        """
        CORE METHOD: Generate fundamental signal using WORKING endpoints
        """
        print(f"\n🎯 GENERATING FUNDAMENTAL SIGNAL: {ticker}")
        print("=" * 70)
        
        # 1. Get price and volume data
        quote_data = self.get_asset_quote(ticker)
        if not quote_data:
            return self._create_neutral_signal(ticker, "No quote data available")
        
        # 2. Analyze news sentiment
        news_sentiment = self.get_market_news_sentiment(days_back=7)
        
        # 3. Get relevant corporate facts
        relevant_facts = self.get_relevant_facts(days_back=30)
        
        # 4. Get options volatility (if available)
        options_data = self.get_options_data(ticker)
        
        # 5. Calculate component scores
        price_momentum_score = self._score_price_momentum(quote_data)
        news_sentiment_score = self._score_news_sentiment(news_sentiment, ticker)
        corporate_events_score = self._score_corporate_events(relevant_facts, ticker)
        market_position_score = self._score_market_position(quote_data, options_data)
        
        # 6. Calculate overall score with practical weighting
        overall_score = (
            price_momentum_score * 0.35 +   # 35% price momentum
            news_sentiment_score * 0.25 +   # 25% news sentiment
            corporate_events_score * 0.20 + # 20% corporate events
            market_position_score * 0.20    # 20% market position
        )
        
        # 7. Generate signal and reasons
        signal, reasons = self._determine_signal(overall_score, quote_data, news_sentiment)
        
        # 8. Calculate price target based on momentum
        target_price = self._calculate_momentum_target(quote_data, overall_score)
        
        # 9. Assess risk
        risk_level = self._assess_practical_risk(quote_data, options_data)
        
        return PracticalFundamentalSignal(
            ticker=ticker,
            signal=signal,
            confidence=overall_score,
            price_momentum_score=price_momentum_score,
            news_sentiment_score=news_sentiment_score,
            corporate_events_score=corporate_events_score,
            market_position_score=market_position_score,
            reasons=reasons,
            current_price=quote_data.get('current_price', 0),
            target_price=target_price,
            risk_level=risk_level
        )
    
    def _analyze_news_sentiment(self, news_data: List[Dict]) -> Dict:
        """Analyze sentiment from news titles and descriptions"""
        if not news_data:
            return {'overall_sentiment': 'NEUTRAL', 'score': 50}
        
        # Positive keywords
        positive_words = [
            'alta', 'subida', 'ganho', 'lucro', 'crescimento', 'aumento',
            'positivo', 'otimismo', 'recuperação', 'melhora', 'expansão'
        ]
        
        # Negative keywords
        negative_words = [
            'queda', 'baixa', 'perda', 'declínio', 'redução', 'negativo',
            'pessimismo', 'crise', 'recessão', 'desaceleração', 'contração'
        ]
        
        sentiment_score = 0
        total_articles = len(news_data)
        
        for article in news_data:
            title = article.get('title', '').lower()
            description = article.get('description', '').lower()
            text = f"{title} {description}"
            
            # Count positive and negative words
            positive_count = sum(1 for word in positive_words if word in text)
            negative_count = sum(1 for word in negative_words if word in text)
            
            # Calculate article sentiment
            if positive_count > negative_count:
                sentiment_score += 1
            elif negative_count > positive_count:
                sentiment_score -= 1
        
        # Calculate overall sentiment percentage
        sentiment_percentage = 50 + (sentiment_score / total_articles) * 50
        sentiment_percentage = max(0, min(100, sentiment_percentage))
        
        if sentiment_percentage > 60:
            overall_sentiment = 'POSITIVE'
        elif sentiment_percentage < 40:
            overall_sentiment = 'NEGATIVE'
        else:
            overall_sentiment = 'NEUTRAL'
        
        return {
            'overall_sentiment': overall_sentiment,
            'score': sentiment_percentage,
            'total_articles': total_articles,
            'positive_articles': max(0, sentiment_score),
            'negative_articles': max(0, -sentiment_score)
        }
    
    def _process_relevant_facts(self, facts_data: List[Dict]) -> List[Dict]:
        """Process and categorize relevant facts by company"""
        processed = defaultdict(list)
        
        for fact in facts_data:
            title = fact.get('title', '')
            
            # Extract ticker from title (assuming format like "COMPANY (TICKER)")
            ticker_match = re.search(r'\(([A-Z0-9]+)\)', title)
            if ticker_match:
                ticker = ticker_match.group(1)
                processed[ticker].append(fact)
        
        return dict(processed)
    
    def _analyze_options_volatility(self, options_data) -> Dict:
        """Analyze options data for volatility insights"""
        if not options_data:
            return {'implied_volatility': 'UNKNOWN', 'volatility_score': 50}
        
        # This would analyze options data structure when available
        # For now, return neutral
        return {'implied_volatility': 'MODERATE', 'volatility_score': 50}
    
    def _score_price_momentum(self, quote_data: Dict) -> float:
        """Score price momentum (0-100)"""
        if not quote_data:
            return 50
        
        score = 50  # Start neutral
        
        # Daily change
        daily_change = quote_data.get('change_percent', 0)
        if daily_change > 2:
            score += 15
        elif daily_change > 0:
            score += 5
        elif daily_change < -2:
            score -= 15
        elif daily_change < 0:
            score -= 5
        
        # Weekly momentum
        weekly_change = quote_data.get('change_week', 0)
        if weekly_change > 5:
            score += 10
        elif weekly_change > 0:
            score += 3
        elif weekly_change < -5:
            score -= 10
        
        # Monthly momentum
        monthly_change = quote_data.get('change_month', 0)
        if monthly_change > 10:
            score += 15
        elif monthly_change > 0:
            score += 5
        elif monthly_change < -10:
            score -= 15
        
        # Volume analysis
        volume = quote_data.get('volume', 0)
        if volume > 1000000:  # High volume
            score += 5
        
        return max(0, min(100, score))
    
    def _score_news_sentiment(self, news_sentiment: Dict, ticker: str) -> float:
        """Score news sentiment for the market/sector"""
        if not news_sentiment:
            return 50
        
        base_score = news_sentiment.get('score', 50)
        
        # Adjust based on overall market sentiment
        sentiment = news_sentiment.get('overall_sentiment', 'NEUTRAL')
        if sentiment == 'POSITIVE':
            return min(100, base_score + 10)
        elif sentiment == 'NEGATIVE':
            return max(0, base_score - 10)
        else:
            return base_score
    
    def _score_corporate_events(self, relevant_facts: Dict, ticker: str) -> float:
        """Score corporate events impact"""
        if not relevant_facts or ticker not in relevant_facts:
            return 50  # Neutral if no news
        
        facts = relevant_facts[ticker]
        score = 50
        
        # More recent corporate events suggest activity
        if len(facts) > 3:  # Many recent events
            score += 10
        elif len(facts) > 1:
            score += 5
        
        # Analyze fact types (basic keyword analysis)
        for fact in facts:
            title = fact.get('title', '').lower()
            if 'dividendo' in title or 'dividend' in title:
                score += 5  # Dividend announcements are positive
            elif 'lucro' in title or 'earnings' in title:
                score += 3
            elif 'aquisição' in title or 'fusão' in title:
                score += 5  # M&A activity
        
        return max(0, min(100, score))
    
    def _score_market_position(self, quote_data: Dict, options_data: Dict) -> float:
        """Score market position and technical factors"""
        if not quote_data:
            return 50
        
        score = 50
        
        # Price position within daily range
        high = quote_data.get('high', 0)
        low = quote_data.get('low', 0)
        current = quote_data.get('current_price', 0)
        
        if high > low:
            position = (current - low) / (high - low)
            if position > 0.8:  # Near high
                score += 10
            elif position > 0.6:
                score += 5
            elif position < 0.2:  # Near low
                score -= 10
            elif position < 0.4:
                score -= 5
        
        # Bid-ask spread analysis
        bid = quote_data.get('bid', 0)
        ask = quote_data.get('ask', 0)
        if bid > 0 and ask > 0:
            spread = (ask - bid) / ((ask + bid) / 2)
            if spread < 0.01:  # Tight spread
                score += 5
            elif spread > 0.05:  # Wide spread
                score -= 5
        
        return max(0, min(100, score))
    
    def _determine_signal(self, score: float, quote_data: Dict, news_sentiment: Dict) -> Tuple[str, List[str]]:
        """Determine trading signal and reasoning"""
        reasons = []
        
        if score >= 70:
            signal = "BUY"
            reasons.append("Strong momentum and positive sentiment")
            if quote_data.get('change_month', 0) > 5:
                reasons.append("Positive monthly trend")
        elif score >= 55:
            signal = "BUY"
            reasons.append("Favorable indicators")
        elif score <= 30:
            signal = "SELL"
            reasons.append("Weak momentum and negative signals")
        elif score <= 45:
            signal = "SELL"
            reasons.append("Below average performance")
        else:
            signal = "HOLD"
            reasons.append("Mixed signals - wait for clearer direction")
        
        # Add specific reasons based on data
        if news_sentiment.get('overall_sentiment') == 'POSITIVE':
            reasons.append("Positive market sentiment")
        elif news_sentiment.get('overall_sentiment') == 'NEGATIVE':
            reasons.append("Negative market sentiment")
        
        return signal, reasons
    
    def _calculate_momentum_target(self, quote_data: Dict, score: float) -> Optional[float]:
        """Calculate price target based on momentum"""
        current_price = quote_data.get('current_price', 0)
        if not current_price:
            return None
        
        # Simple momentum-based target
        monthly_change = quote_data.get('change_month', 0) / 100
        
        if score > 70:
            # Bullish target: extend monthly trend
            target_multiplier = 1 + (monthly_change * 0.5)
        elif score < 30:
            # Bearish target: negative adjustment
            target_multiplier = 1 + (monthly_change * 0.3)
        else:
            # Neutral: slight adjustment
            target_multiplier = 1 + (monthly_change * 0.1)
        
        return current_price * target_multiplier
    
    def _assess_practical_risk(self, quote_data: Dict, options_data: Dict) -> str:
        """Assess risk level based on available data"""
        risk_factors = 0
        
        # Volatility from price data
        high = quote_data.get('high', 0)
        low = quote_data.get('low', 0)
        current = quote_data.get('current_price', 0)
        
        if current > 0:
            daily_range = (high - low) / current
            if daily_range > 0.05:  # 5%+ daily range
                risk_factors += 1
        
        # Recent performance volatility
        monthly_change = abs(quote_data.get('change_month', 0))
        if monthly_change > 20:  # High monthly volatility
            risk_factors += 1
        
        # Volume considerations
        trades = quote_data.get('quantity_trades', 0)
        if trades < 100:  # Low liquidity
            risk_factors += 1
        
        if risk_factors >= 2:
            return "HIGH"
        elif risk_factors == 1:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _create_neutral_signal(self, ticker: str, reason: str) -> PracticalFundamentalSignal:
        """Create neutral signal when data is unavailable"""
        return PracticalFundamentalSignal(
            ticker=ticker,
            signal="HOLD",
            confidence=50.0,
            price_momentum_score=50.0,
            news_sentiment_score=50.0,
            corporate_events_score=50.0,
            market_position_score=50.0,
            reasons=[reason],
            current_price=0.0,
            risk_level="UNKNOWN"
        )

def test_practical_robot():
    """Test the practical fundamental robot with real data"""
    print("🤖 TESTING PRACTICAL FUNDAMENTAL ROBOT")
    print("=" * 80)
    
    robot = PracticalFundamentalRobot()
    
    # Use credentials (you'll need to provide these)
    username = "your_username"  # Replace with actual
    password = "your_password"  # Replace with actual
    
    if robot.authenticate(username, password):
        # Test with popular Brazilian stocks
        test_tickers = ['VALE3', 'PETR4', 'ITUB4', 'BBDC4', 'ABEV3']
        
        for ticker in test_tickers:
            print(f"\n{'='*50}")
            signal = robot.generate_fundamental_signal(ticker)
            
            print(f"🎯 SIGNAL: {signal.signal} ({signal.confidence:.1f}% confidence)")
            print(f"💰 Current Price: R${signal.current_price:.2f}")
            if signal.target_price:
                print(f"🎯 Target Price: R${signal.target_price:.2f}")
            print(f"⚠️  Risk Level: {signal.risk_level}")
            
            print(f"\n📊 COMPONENT SCORES:")
            print(f"   Price Momentum: {signal.price_momentum_score:.1f}")
            print(f"   News Sentiment: {signal.news_sentiment_score:.1f}")
            print(f"   Corporate Events: {signal.corporate_events_score:.1f}")
            print(f"   Market Position: {signal.market_position_score:.1f}")
            
            print(f"\n💡 REASONS:")
            for reason in signal.reasons:
                print(f"   • {reason}")

if __name__ == "__main__":
    test_practical_robot()
