#!/usr/bin/env python3
"""
Options Trading Filter & Analysis System
Filters and analyzes options data to identify tradeable opportunities
"""

import json
import os
from typing import Dict, List, Tuple
from datetime import datetime

class OptionsTradeabilityAnalyzer:
    def __init__(self):
        self.min_open_interest = 1000
        self.min_volume = 50
        self.max_spread_percent = 10
        self.min_option_price = 0.01
        
    def load_options_data(self, file_path: str) -> Dict:
        """Load options discovery results"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading options data: {e}")
            return {}
    
    def analyze_option_quality(self, option: Dict) -> Dict:
        """Analyze individual option for trading quality"""
        analysis = {
            'symbol': option.get('symbol', ''),
            'is_tradeable': False,
            'quality_score': 0,
            'warnings': [],
            'strengths': [],
            'liquidity_rating': 'POOR'
        }
        
        # Extract key metrics
        open_interest = option.get('open_interest', 0)
        volume = option.get('volume', 0)
        bid = option.get('bid', 0)
        ask = option.get('ask', 0)
        last_trade = option.get('last_trade', 0)
        
        # Quality scoring (0-100)
        score = 0
        
        # Open Interest Analysis
        if open_interest >= 10000:
            score += 30
            analysis['strengths'].append(f"Excellent open interest: {open_interest:,}")
            analysis['liquidity_rating'] = 'EXCELLENT'
        elif open_interest >= 5000:
            score += 25
            analysis['strengths'].append(f"Good open interest: {open_interest:,}")
            analysis['liquidity_rating'] = 'GOOD'
        elif open_interest >= 1000:
            score += 15
            analysis['strengths'].append(f"Acceptable open interest: {open_interest:,}")
            analysis['liquidity_rating'] = 'ACCEPTABLE'
        elif open_interest > 0:
            score += 5
            analysis['warnings'].append(f"Low open interest: {open_interest:,}")
            analysis['liquidity_rating'] = 'LOW'
        else:
            analysis['warnings'].append("ZERO open interest - DEAD option!")
            analysis['liquidity_rating'] = 'DEAD'
        
        # Volume Analysis
        if volume >= 500:
            score += 25
            analysis['strengths'].append(f"High volume: {volume}")
        elif volume >= 100:
            score += 20
            analysis['strengths'].append(f"Good volume: {volume}")
        elif volume >= 50:
            score += 10
            analysis['strengths'].append(f"Moderate volume: {volume}")
        elif volume > 0:
            score += 5
            analysis['warnings'].append(f"Low volume: {volume}")
        else:
            analysis['warnings'].append("ZERO volume today")
        
        # Bid/Ask Analysis
        if bid > 0 and ask > 0:
            spread = ask - bid
            spread_percent = (spread / ask) * 100 if ask > 0 else 100
            
            if spread_percent <= 5:
                score += 20
                analysis['strengths'].append(f"Tight spread: {spread_percent:.1f}%")
            elif spread_percent <= 10:
                score += 15
                analysis['strengths'].append(f"Acceptable spread: {spread_percent:.1f}%")
            else:
                score += 5
                analysis['warnings'].append(f"Wide spread: {spread_percent:.1f}%")
        elif bid > 0 or ask > 0:
            score += 5
            analysis['warnings'].append("One-sided market (bid OR ask only)")
        else:
            analysis['warnings'].append("NO bid/ask quotes - can't trade at market")
        
        # Price Analysis
        if last_trade >= 0.10:
            score += 15
            analysis['strengths'].append(f"Good option price: R${last_trade:.2f}")
        elif last_trade > 0:
            score += 5
            analysis['warnings'].append(f"Low option price: R${last_trade:.2f}")
        else:
            analysis['warnings'].append("NO recent trades")
        
        # Final Tradeability Assessment
        analysis['quality_score'] = score
        
        if score >= 70:
            analysis['is_tradeable'] = True
            analysis['overall_rating'] = 'EXCELLENT'
        elif score >= 50:
            analysis['is_tradeable'] = True
            analysis['overall_rating'] = 'GOOD'
        elif score >= 30:
            analysis['is_tradeable'] = True
            analysis['overall_rating'] = 'ACCEPTABLE'
        elif score >= 15:
            analysis['is_tradeable'] = False
            analysis['overall_rating'] = 'POOR'
        else:
            analysis['is_tradeable'] = False
            analysis['overall_rating'] = 'AVOID'
        
        return analysis
    
    def filter_tradeable_options(self, options_data: Dict) -> Dict:
        """Filter and rank all options by tradeability"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'total_options_analyzed': 0,
            'tradeable_options': [],
            'avoided_options': [],
            'summary': {
                'excellent_count': 0,
                'good_count': 0,
                'acceptable_count': 0,
                'poor_count': 0,
                'avoid_count': 0
            }
        }
        
        for company, data in options_data.items():
            if 'options' not in data:
                continue
                
            print(f"\n🔍 Analyzing {company} options...")
            
            for option in data['options']:
                results['total_options_analyzed'] += 1
                analysis = self.analyze_option_quality(option)
                
                # Add original option data
                analysis['option_data'] = option
                
                if analysis['is_tradeable']:
                    results['tradeable_options'].append(analysis)
                else:
                    results['avoided_options'].append(analysis)
                
                # Update summary counts
                rating = analysis['overall_rating']
                if rating == 'EXCELLENT':
                    results['summary']['excellent_count'] += 1
                elif rating == 'GOOD':
                    results['summary']['good_count'] += 1
                elif rating == 'ACCEPTABLE':
                    results['summary']['acceptable_count'] += 1
                elif rating == 'POOR':
                    results['summary']['poor_count'] += 1
                else:
                    results['summary']['avoid_count'] += 1
        
        # Sort tradeable options by quality score
        results['tradeable_options'].sort(key=lambda x: x['quality_score'], reverse=True)
        
        return results
    
    def print_trading_recommendations(self, filtered_results: Dict):
        """Print actionable trading recommendations"""
        print("\n" + "="*80)
        print("🎯 OPTIONS TRADING ANALYSIS RESULTS")
        print("="*80)
        
        total = filtered_results['total_options_analyzed']
        tradeable = len(filtered_results['tradeable_options'])
        avoided = len(filtered_results['avoided_options'])
        
        print(f"\n📊 SUMMARY:")
        print(f"   Total Options Analyzed: {total}")
        print(f"   Tradeable Options: {tradeable} ({tradeable/total*100:.1f}%)")
        print(f"   Options to Avoid: {avoided} ({avoided/total*100:.1f}%)")
        
        summary = filtered_results['summary']
        print(f"\n📈 QUALITY BREAKDOWN:")
        print(f"   🟢 Excellent: {summary['excellent_count']}")
        print(f"   🔵 Good: {summary['good_count']}")
        print(f"   🟡 Acceptable: {summary['acceptable_count']}")
        print(f"   🟠 Poor: {summary['poor_count']}")
        print(f"   🔴 Avoid: {summary['avoid_count']}")
        
        # Show top tradeable options
        if filtered_results['tradeable_options']:
            print(f"\n🏆 TOP 5 TRADEABLE OPTIONS:")
            print("-" * 80)
            
            for i, option in enumerate(filtered_results['tradeable_options'][:5]):
                data = option['option_data']
                print(f"\n{i+1}. {option['symbol']} (Score: {option['quality_score']}/100)")
                print(f"   Rating: {option['overall_rating']} | Liquidity: {option['liquidity_rating']}")
                print(f"   Open Interest: {data['open_interest']:,} | Volume: {data['volume']}")
                print(f"   Last Trade: R${data['last_trade']:.2f} | Bid/Ask: {data['bid']:.2f}/{data['ask']:.2f}")
                print(f"   ✅ Strengths: {', '.join(option['strengths'])}")
                if option['warnings']:
                    print(f"   ⚠️  Warnings: {', '.join(option['warnings'])}")
        
        print(f"\n🚨 BEGINNER RECOMMENDATIONS:")
        print("   1. Start with options rated 'EXCELLENT' or 'GOOD'")
        print("   2. Never trade options with 0 open interest")
        print("   3. Focus on VALE options (most liquid in Brazilian market)")
        print("   4. Start with small positions (1-2 contracts)")
        print("   5. Always check bid/ask spread before trading")

def main():
    analyzer = OptionsTradeabilityAnalyzer()
    
    # Load the options discovery results
    results_file = "options_discovery_results.json"
    if not os.path.exists(results_file):
        print(f"❌ Options results file not found: {results_file}")
        print("   Run automated_options_discovery.py first!")
        return
    
    print("🔍 Loading options discovery results...")
    options_data = analyzer.load_options_data(results_file)
    
    if not options_data:
        print("❌ No options data found!")
        return
    
    print("📊 Filtering and analyzing options for tradeability...")
    filtered_results = analyzer.filter_tradeable_options(options_data)
    
    # Save filtered results
    output_file = "tradeable_options_analysis.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(filtered_results, f, indent=2, ensure_ascii=False)
    
    # Print recommendations
    analyzer.print_trading_recommendations(filtered_results)
    
    print(f"\n💾 Detailed analysis saved to: {output_file}")
    
    # Quick stats for integration
    tradeable_count = len(filtered_results['tradeable_options'])
    if tradeable_count > 0:
        print(f"\n🎯 READY FOR ROBOT INTEGRATION:")
        print(f"   Found {tradeable_count} tradeable options")
        print(f"   Best option: {filtered_results['tradeable_options'][0]['symbol']}")
        print(f"   Top score: {filtered_results['tradeable_options'][0]['quality_score']}/100")

if __name__ == "__main__":
    main()
