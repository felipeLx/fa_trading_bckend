#!/usr/bin/env python3
"""
Manual PETR4 Geopolitical Opportunity Analysis
Special analysis for Iran conflict oil opportunity
"""

import sys
import os
from datetime import datetime, timedelta

# Add the current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def analyze_petr4_opportunity():
    """Analyze PETR4 for geopolitical oil opportunity"""
    print("🛢️ PETR4 GEOPOLITICAL OPPORTUNITY ANALYSIS")
    print("=" * 60)
    print(f"📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🌍 Context: Iran conflict driving oil prices higher")
    
    # Market data from Felipe's research
    market_data = {
        "PETR4_futures_gain": 7.51,  # %
        "brent_price": 73.915,       # USD
        "brent_gain": 5.74,          # %
        "wti_gain": 6.29,            # %
        "petr4_week_range": {"min": 29.00, "max": 31.24, "open": 29.70}
    }
    
    print(f"\n📊 CURRENT MARKET CONDITIONS:")
    print(f"   🛢️ PETR4 Futures: +{market_data['PETR4_futures_gain']:.2f}%")
    print(f"   🌍 Brent Crude: ${market_data['brent_price']:.3f} (+{market_data['brent_gain']:.2f}%)")
    print(f"   🇺🇸 WTI Crude: +{market_data['wti_gain']:.2f}%")
    print(f"   📈 PETR4 Range: {market_data['petr4_week_range']['min']:.2f} - {market_data['petr4_week_range']['max']:.2f}")
    
    # Try to get current robot signal for PETR4
    try:
        from integrated_cedrotech_robot import IntegratedCedroTechRobot
        
        print(f"\n🤖 ROBOT SIGNAL ANALYSIS:")
        robot = IntegratedCedroTechRobot(paper_trading=True)
        
        # Check if PETR4 is in asset universe
        if 'PETR4' in robot.asset_universe:
            print(f"   ✅ PETR4 is monitored by robot")
            
            try:
                # Get current analysis
                analysis = robot.get_combined_analysis('PETR4')
                
                print(f"   📊 Current Signal: {analysis['signal']}")
                print(f"   🎯 Confidence: {analysis['confidence']:.1f}%")
                print(f"   📈 Fundamental: {analysis['fundamental']['signal']} ({analysis['fundamental']['confidence']:.1f}%)")
                print(f"   📉 Technical: {analysis['technical']['signal']} ({analysis['technical']['confidence']:.1f}%)")
                
                # Enhanced analysis for geopolitical context
                print(f"\n🌍 GEOPOLITICAL ENHANCEMENT:")
                
                # Calculate geopolitical boost
                base_confidence = analysis['confidence']
                geopolitical_boost = 0
                
                # Oil surge boost
                if market_data['brent_gain'] > 5.0:
                    geopolitical_boost += 15
                    print(f"   ⚡ Oil surge boost: +15 points")
                
                # PETR4 specific performance
                if market_data['PETR4_futures_gain'] > 7.0:
                    geopolitical_boost += 10
                    print(f"   🛢️ PETR4 momentum boost: +10 points")
                
                # Conflict duration assessment
                geopolitical_boost += 10  # Long-term conflict premium
                print(f"   ⏳ Long-term conflict premium: +10 points")
                
                enhanced_confidence = min(95, base_confidence + geopolitical_boost)
                
                print(f"\n📊 ENHANCED ANALYSIS:")
                print(f"   🎯 Base Robot Confidence: {base_confidence:.1f}%")
                print(f"   🌍 Geopolitical Boost: +{geopolitical_boost} points")
                print(f"   💪 Enhanced Confidence: {enhanced_confidence:.1f}%")
                
                return {
                    'symbol': 'PETR4',
                    'base_signal': analysis['signal'],
                    'base_confidence': base_confidence,
                    'enhanced_confidence': enhanced_confidence,
                    'geopolitical_boost': geopolitical_boost,
                    'recommendation': 'STRONG_BUY' if enhanced_confidence >= 80 else 'BUY' if enhanced_confidence >= 70 else 'HOLD'
                }
                
            except Exception as e:
                print(f"   ❌ Error getting robot analysis: {e}")
                return None
        else:
            print(f"   ⚠️ PETR4 not in robot universe")
            return None
            
    except Exception as e:
        print(f"❌ Robot analysis failed: {e}")
        return None

def calculate_position_sizing(account_balance=500, risk_percent=5.0):
    """Calculate position sizing for PETR4 trade - CORRECTED VERSION"""
    print(f"\n💰 POSITION SIZING ANALYSIS:")
    print(f"   💵 Account Balance: R${account_balance:.2f}")
    print(f"   🎯 Risk Tolerance: {risk_percent:.1f}%")
    
    # Assume PETR4 current price around R$30.00 (from futures data)
    estimated_price = 30.00
    risk_amount = account_balance * (risk_percent / 100)
    
    # Conservative stop loss for geopolitical trades
    stop_loss_percent = 4.0  # 4% stop loss
    stop_loss_distance = estimated_price * (stop_loss_percent / 100)
    
    # CORRECTED: Calculate position size based on TOTAL AVAILABLE CAPITAL
    max_shares_by_capital = int(account_balance / estimated_price)  # What we can afford
    max_shares_by_risk = int(risk_amount / stop_loss_distance)      # What risk allows
    
    # Take the SMALLER of the two (safer approach)
    max_shares = min(max_shares_by_capital, max_shares_by_risk)
    total_investment = max_shares * estimated_price
    actual_risk_percent = (total_investment / account_balance) * 100    
    print(f"   📊 Estimated PETR4 Price: R${estimated_price:.2f}")
    print(f"   🛑 Stop Loss: {stop_loss_percent:.1f}% (R${stop_loss_distance:.2f})")
    print(f"   💰 Max by Capital: {max_shares_by_capital} shares (R${max_shares_by_capital * estimated_price:.2f})")
    print(f"   🎯 Max by Risk: {max_shares_by_risk} shares (R${max_shares_by_risk * estimated_price:.2f})")
    print(f"   📦 SAFE Position Size: {max_shares} shares")
    print(f"   💰 Total Investment: R${total_investment:.2f}")
    print(f"   📊 Capital Usage: {actual_risk_percent:.1f}% of account")
    
    # Add safety warnings
    if actual_risk_percent > 80:
        print(f"   ⚠️ WARNING: High capital usage ({actual_risk_percent:.1f}%)")
    if total_investment > account_balance * 0.9:
        print(f"   🚨 CAUTION: Using >90% of available capital")
    
    return {
        'shares': max_shares,
        'investment': total_investment,
        'risk_percent': actual_risk_percent,
        'stop_loss': estimated_price - stop_loss_distance,
        'max_by_capital': max_shares_by_capital,
        'max_by_risk': max_shares_by_risk
    }

def geopolitical_trading_recommendation():
    """Generate final recommendation"""
    print(f"\n🎯 GEOPOLITICAL TRADING RECOMMENDATION:")
    
    # Analyze the opportunity
    analysis = analyze_petr4_opportunity()
    position = calculate_position_sizing()
    
    if analysis and analysis['enhanced_confidence'] >= 75:
        print(f"\n✅ RECOMMENDATION: {analysis['recommendation']}")
        print(f"   🎯 Enhanced Confidence: {analysis['enhanced_confidence']:.1f}%")
        print(f"   📦 Suggested Position: {position['shares']} shares")
        print(f"   💰 Investment Amount: R${position['investment']:.2f}")
        print(f"   🛑 Stop Loss: R${position['stop_loss']:.2f}")
        
        print(f"\n🔥 RATIONALE:")
        print(f"   🌍 Iran conflict creating oil supply concerns")
        print(f"   📈 PETR4 futures already up +7.51%")
        print(f"   🛢️ Brent crude surge (+5.74%) benefits Petrobras")
        print(f"   ⏳ Long-term conflict suggests sustained higher prices")
        print(f"   🎯 Robot signals enhanced by geopolitical context")
        
        print(f"\n⚠️ RISKS TO CONSIDER:")
        print(f"   🕊️ Conflict resolution could reverse gains quickly")
        print(f"   📉 Oil price volatility is high")
        print(f"   💰 Using real money vs current paper trading")
        print(f"   📊 Economic factors beyond geopolitics")
        
        return True
    else:
        print(f"\n⚠️ RECOMMENDATION: WAIT")
        print(f"   📊 Confidence too low for real money trade")
        print(f"   🎯 Current signals don't support high-conviction play")
        return False

if __name__ == "__main__":
    should_trade = geopolitical_trading_recommendation()
    
    if should_trade:
        print(f"\n🚀 NEXT STEPS:")
        print(f"   1. Monitor Iran conflict development")
        print(f"   2. Check PETR4 opening price tomorrow")
        print(f"   3. Consider switching robot to live trading for this opportunity")
        print(f"   4. Set tight stop losses given volatility")
    else:
        print(f"\n🔄 ALTERNATIVE APPROACH:")
        print(f"   1. Let robot continue paper trading")
        print(f"   2. Watch for stronger signals")
        print(f"   3. Monitor geopolitical developments")
        print(f"   4. Wait for higher confidence entry point")
