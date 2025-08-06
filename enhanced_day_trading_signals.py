"""
Enhanced Day Trading Signal Generation
Fixes the overly conservative signal logic that prevents the robot from trading
"""

import numpy as np
from typing import List, Dict, Tuple, Optional

def calculate_rsi(prices: List[float], period: int = 14) -> Optional[float]:
    """Calculate RSI for signal generation."""
    if len(prices) < period + 1:
        return None
    
    deltas = np.diff(prices)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    
    avg_gain = np.mean(gains[:period])
    avg_loss = np.mean(losses[:period])
    
    if avg_loss == 0:
        return 100
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_moving_averages(prices: List[float]) -> Tuple[Optional[float], Optional[float]]:
    """Calculate short and long term moving averages."""
    if len(prices) < 20:
        return None, None
    
    ma_5 = np.mean(prices[-5:])  # Short term
    ma_20 = np.mean(prices[-20:])  # Long term
    return ma_5, ma_20

def enhanced_day_trading_signal(prices: List[Dict]) -> Tuple[str, float, Dict]:
    """
    Enhanced day trading signal generation - MUCH MORE AGGRESSIVE
    
    Returns:
        signal: 'buy', 'sell', or 'hold'
        confidence: 0-100 confidence score
        details: Signal breakdown for debugging
    """
    if not prices or len(prices) < 5:
        return 'hold', 0, {'error': 'Insufficient price data'}
    
    # Extract price data
    closes = [p['close'] for p in prices if p.get('close', 0) > 0]
    highs = [p['high'] for p in prices if p.get('high', 0) > 0]
    lows = [p['low'] for p in prices if p.get('low', 0) > 0]
    volumes = [p.get('volume', 0) for p in prices]
    
    if len(closes) < 5:
        return 'hold', 0, {'error': 'Insufficient valid price data'}
    
    current_price = closes[-1]
    recent_high = max(highs[-10:]) if len(highs) >= 10 else max(highs)
    recent_low = min(lows[-10:]) if len(lows) >= 10 else min(lows)
    
    # Technical indicators
    rsi = calculate_rsi(closes)
    ma_short, ma_long = calculate_moving_averages(closes)
    
    # Price momentum
    price_change_5m = (closes[-1] - closes[-2]) / closes[-2] * 100 if len(closes) >= 2 else 0
    price_change_1h = (closes[-1] - closes[-6]) / closes[-6] * 100 if len(closes) >= 6 else 0
    
    # Volume analysis
    current_volume = volumes[-1] if volumes else 0
    avg_volume = np.mean(volumes[-10:]) if len(volumes) >= 10 else current_volume
    volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
    
    # Signal calculation (0-100 score)
    signal_score = 50  # Start neutral
    reasons = []
    
    # 1. RSI-based signals (day trading friendly)
    if rsi is not None:
        if 25 <= rsi <= 45:  # Oversold but not extreme (BUY ZONE)
            signal_score += 20
            reasons.append(f"Oversold RSI ({rsi:.1f}) - good entry")
        elif 55 <= rsi <= 75:  # Overbought but not extreme (SELL ZONE)
            signal_score -= 15
            reasons.append(f"Overbought RSI ({rsi:.1f}) - consider exit")
        elif rsi < 25:  # Extremely oversold (STRONG BUY)
            signal_score += 30
            reasons.append(f"Extremely oversold RSI ({rsi:.1f}) - strong buy")
        elif rsi > 75:  # Extremely overbought (STRONG SELL)
            signal_score -= 25
            reasons.append(f"Extremely overbought RSI ({rsi:.1f}) - strong sell")
    
    # 2. Moving average signals
    if ma_short and ma_long:
        if ma_short > ma_long:  # Uptrend
            signal_score += 15
            reasons.append("Short MA > Long MA (uptrend)")
        else:  # Downtrend
            signal_score -= 10
            reasons.append("Short MA < Long MA (downtrend)")
        
        # Price position relative to MA
        if current_price > ma_short:
            signal_score += 10
            reasons.append("Price above short MA")
        else:
            signal_score += 5  # Still okay for day trading entry
            reasons.append("Price below short MA (potential entry)")
    
    # 3. Price momentum (KEY FOR DAY TRADING)
    if price_change_5m > 0.5:  # Rising in last 5 minutes
        signal_score += 15
        reasons.append(f"Rising momentum (+{price_change_5m:.1f}% in 5m)")
    elif price_change_5m < -0.5:  # Falling in last 5 minutes
        signal_score -= 10
        reasons.append(f"Falling momentum ({price_change_5m:.1f}% in 5m)")
    
    # 4. Price position in range (AGGRESSIVE DAY TRADING)
    price_position = (current_price - recent_low) / (recent_high - recent_low) if recent_high > recent_low else 0.5
    
    if 0.2 <= price_position <= 0.6:  # Sweet spot for entries (20-60% of range)
        signal_score += 20
        reasons.append(f"Good entry position ({price_position*100:.0f}% of range)")
    elif price_position < 0.2:  # Near lows (STRONG BUY)
        signal_score += 25
        reasons.append(f"Near recent lows ({price_position*100:.0f}% of range) - strong buy")
    elif price_position > 0.8:  # Near highs (AVOID/SELL)
        signal_score -= 20
        reasons.append(f"Near recent highs ({price_position*100:.0f}% of range) - avoid")
    
    # 5. Volume confirmation
    if volume_ratio > 1.2:  # Above average volume
        signal_score += 10
        reasons.append(f"High volume ({volume_ratio:.1f}x average)")
    elif volume_ratio < 0.8:  # Below average volume
        signal_score -= 5
        reasons.append(f"Low volume ({volume_ratio:.1f}x average)")
    
    # 6. Hour-based momentum
    if abs(price_change_1h) > 2:  # Significant movement in past hour
        if price_change_1h > 0:
            signal_score += 10
            reasons.append(f"Strong hourly rise (+{price_change_1h:.1f}%)")
        else:
            signal_score -= 5
            reasons.append(f"Hourly decline ({price_change_1h:.1f}%)")
    
    # Final signal determination (MUCH MORE AGGRESSIVE)
    confidence = min(100, max(0, signal_score))
    
    if signal_score >= 70:
        signal = 'buy'
    elif signal_score <= 30:
        signal = 'sell'
    else:
        signal = 'hold'
    
    details = {
        'signal_score': signal_score,
        'rsi': rsi,
        'ma_short': ma_short,
        'ma_long': ma_long,
        'price_position': price_position,
        'volume_ratio': volume_ratio,
        'price_change_5m': price_change_5m,
        'price_change_1h': price_change_1h,
        'recent_high': recent_high,
        'recent_low': recent_low,
        'current_price': current_price,
        'reasons': reasons
    }
    
    return signal, confidence, details

def test_signal_generation():
    """Test the new signal generation with sample data."""
    # Sample price data (simulating EMBR3 recent prices)
    sample_prices = [
        {'close': 65.0, 'high': 65.5, 'low': 64.8, 'volume': 1000000},
        {'close': 64.8, 'high': 65.2, 'low': 64.5, 'volume': 1200000},
        {'close': 64.9, 'high': 65.0, 'low': 64.7, 'volume': 900000},
        {'close': 65.1, 'high': 65.3, 'low': 64.9, 'volume': 1100000},
        {'close': 65.2, 'high': 65.4, 'low': 65.0, 'volume': 800000},
        {'close': 65.0, 'high': 65.2, 'low': 64.8, 'volume': 1300000},
        {'close': 64.7, 'high': 65.0, 'low': 64.5, 'volume': 1500000},  # Recent dip
        {'close': 64.9, 'high': 65.1, 'low': 64.7, 'volume': 1400000},  # Recovering
    ]
    
    signal, confidence, details = enhanced_day_trading_signal(sample_prices)
    
    print("🔍 ENHANCED SIGNAL ANALYSIS")
    print("=" * 50)
    print(f"Signal: {signal.upper()}")
    print(f"Confidence: {confidence}/100")
    print(f"Signal Score: {details['signal_score']}")
    print(f"Current Price: R${details['current_price']:.2f}")
    print(f"Price Range: R${details['recent_low']:.2f} - R${details['recent_high']:.2f}")
    print(f"Position in Range: {details['price_position']*100:.0f}%")
    if details['rsi']:
        print(f"RSI: {details['rsi']:.1f}")
    print(f"Volume Ratio: {details['volume_ratio']:.1f}x")
    print("\n📋 REASONS:")
    for reason in details['reasons']:
        print(f"  • {reason}")

if __name__ == "__main__":
    test_signal_generation()
