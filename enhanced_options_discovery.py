#!/usr/bin/env python3
"""
Enhanced Options Discovery & Analysis Integration
Senior-level integration that combines active options discovery with quality analysis
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from cedrotech_options_api import CedroTechOptionsAPI
from options_filter_analysis import OptionsTradeabilityAnalyzer

class EnhancedOptionsDiscovery:
    """
    Senior-level options discovery system that:
    1. Discovers active options using wildcard patterns
    2. Applies quality analysis filtering
    3. Returns ranked tradeable options for the robot
    """
    
    def __init__(self):
        self.options_api = CedroTechOptionsAPI()
        self.analyzer = OptionsTradeabilityAnalyzer()
        
        # Brazilian options patterns (comprehensive)
        self.stock_patterns = {
            'VALE3': {
                'calls': ['VALEG', 'VALEH', 'VALEI', 'VALEJ', 'VALEK', 'VALEL'],
                'puts': ['VALEF', 'VALEM', 'VALEN', 'VALEO', 'VALEP', 'VALEQ'],
                'strikes': self._generate_strikes(42, 65, 0.5)  # VALE typical range
            },
            'PETR4': {
                'calls': ['PETRG', 'PETRH', 'PETRI', 'PETRJ', 'PETRK', 'PETRL'],
                'puts': ['PETRF', 'PETRM', 'PETRN', 'PETRO', 'PETRP', 'PETRQ'],
                'strikes': self._generate_strikes(35, 50, 0.5)  # PETROBRAS typical range
            },
            'ITUB4': {
                'calls': ['ITUBG', 'ITUBH', 'ITUBI', 'ITUBJ', 'ITUBK', 'ITUBL'],
                'puts': ['ITUBF', 'ITUBM', 'ITUBN', 'ITUBO', 'ITUBP', 'ITUBQ'],
                'strikes': self._generate_strikes(28, 42, 0.5)  # ITAU typical range
            },
            'BBAS3': {
                'calls': ['BBASG', 'BBASH', 'BBASI', 'BBASJ', 'BBASK', 'BBASL'],
                'puts': ['BBASF', 'BBASM', 'BBASN', 'BBASO', 'BBASP', 'BBASQ'],
                'strikes': self._generate_strikes(22, 38, 0.5)  # BANCO DO BRASIL typical range
            },
            'B3SA3': {
                'calls': ['B3SAG', 'B3SAH', 'B3SAI', 'B3SAJ', 'B3SAK', 'B3SAL'],
                'puts': ['B3SAF', 'B3SAM', 'B3SAN', 'B3SAO', 'B3SAP', 'B3SAQ'],
                'strikes': self._generate_strikes(8, 15, 0.25)  # B3 typical range
            }
        }
        
        # Common expiry codes
        self.expiry_codes = ['W1', 'W2', 'W3', 'W4', 'W5', 'X1', 'X2', 'X3', 'Y1', 'Y2', 'Z1', 'Z2']
        
    def _generate_strikes(self, min_strike: float, max_strike: float, increment: float) -> List[str]:
        """Generate strike price list for a stock"""
        strikes = []
        current = min_strike
        while current <= max_strike:
            # Format as integer for strikes like 45, 46, or with decimals like 45.5
            if current == int(current):
                strikes.append(str(int(current)))
            else:
                strikes.append(f"{current:.1f}".replace('.', ''))  # 45.5 becomes "455"
            current += increment
        return strikes
    
    def discover_active_options(self) -> Dict[str, List[Dict]]:
        """
        Discover all active options using comprehensive pattern matching
        Returns organized data suitable for quality analysis
        """
        print("🔍 ENHANCED OPTIONS DISCOVERY")
        print("=" * 60)
        
        if not self.options_api.authenticate():
            print("❌ Failed to authenticate with CedroTech API")
            return {}
        
        discovered_options = {}
        total_found = 0
        
        for underlying, patterns in self.stock_patterns.items():
            print(f"\n📊 Discovering {underlying} options...")
            
            underlying_options = []
            
            # Search calls and puts
            for option_type in ['calls', 'puts']:
                type_patterns = patterns[option_type]
                print(f"   🔍 Searching {option_type}...")
                
                for pattern in type_patterns[:3]:  # Limit patterns to avoid too many API calls
                    print(f"      Pattern: {pattern}*")
                    pattern_found = 0
                    
                    for strike in patterns['strikes'][:12]:  # Top 12 strikes
                        for expiry in self.expiry_codes[:6]:  # Top 6 expiry codes
                            symbol = f"{pattern}{strike}{expiry}"
                            
                            # Get option data from API
                            result = self.options_api.get_asset_info(symbol)
                            if result.get('success'):
                                data = result.get('data', {})
                                
                                # Extract quote data
                                bid = float(data.get('bid', 0))
                                ask = float(data.get('ask', 0))
                                last_trade = float(data.get('lastTrade', data.get('last', 0)))
                                volume = int(data.get('volume', 0))
                                open_interest = int(data.get('openInterest', data.get('interest', 0)))
                                
                                # Consider active if has any trading data
                                if bid > 0 or ask > 0 or last_trade > 0 or volume > 0 or open_interest > 0:
                                    option_data = {
                                        'symbol': symbol,
                                        'underlying': underlying,
                                        'pattern': pattern,
                                        'strike': strike,
                                        'expiry': expiry,
                                        'type': option_type[:-1],  # 'calls' -> 'call'
                                        'bid': bid,
                                        'ask': ask,
                                        'last_trade': last_trade,
                                        'volume': volume,
                                        'open_interest': open_interest,
                                        'discovery_time': datetime.now().isoformat()
                                    }
                                    
                                    underlying_options.append(option_data)
                                    pattern_found += 1
                                    total_found += 1
                                    
                                    print(f"         ✅ {symbol} - OI: {open_interest:,}, Vol: {volume}")
                    
                    print(f"      Found {pattern_found} options for {pattern}")
            
            if underlying_options:
                discovered_options[underlying] = {'options': underlying_options}
                print(f"   📈 Total {underlying}: {len(underlying_options)} active options")
            else:
                print(f"   ⚠️ No active options found for {underlying}")
        
        print(f"\n🎯 DISCOVERY SUMMARY:")
        print(f"   Total active options found: {total_found}")
        print(f"   Underlyings with options: {len(discovered_options)}")
        
        return discovered_options
    
    def analyze_and_filter_options(self, discovered_options: Dict) -> Dict:
        """
        Apply quality analysis to discovered options
        Returns filtered and ranked tradeable options
        """
        print("\n📊 APPLYING QUALITY ANALYSIS...")
        print("=" * 60)
        
        if not discovered_options:
            print("❌ No options to analyze")
            return {'tradeable_options': [], 'summary': {}}
        
        # Apply the sophisticated filtering from OptionsTradeabilityAnalyzer
        filtered_results = self.analyzer.filter_tradeable_options(discovered_options)
        
        # Additional senior-level filtering
        enhanced_results = self._apply_senior_filters(filtered_results)
        
        return enhanced_results
    
    def _apply_senior_filters(self, results: Dict) -> Dict:
        """
        Apply additional senior-level filters for day trading
        """
        print("🎯 Applying senior-level day trading filters...")
        
        tradeable_options = results.get('tradeable_options', [])
        if not tradeable_options:
            return results
        
        # Senior filters for day trading
        senior_filtered = []
        
        for option in tradeable_options:
            data = option['option_data']
            
            # Day trading specific criteria
            day_trade_score = 0
            senior_warnings = []
            senior_strengths = []
            
            # Liquidity requirements (stricter for day trading)
            if data['open_interest'] >= 5000:
                day_trade_score += 30
                senior_strengths.append("Excellent liquidity for day trading")
            elif data['open_interest'] >= 2000:
                day_trade_score += 20
                senior_strengths.append("Good liquidity for day trading")
            elif data['open_interest'] >= 1000:
                day_trade_score += 10
                senior_warnings.append("Minimum liquidity - trade with caution")
            else:
                senior_warnings.append("Poor liquidity - avoid for day trading")
                continue  # Skip options with poor liquidity
            
            # Volume requirements (must have recent activity)
            if data['volume'] >= 100:
                day_trade_score += 25
                senior_strengths.append("High volume today")
            elif data['volume'] >= 50:
                day_trade_score += 15
                senior_strengths.append("Good volume today")
            elif data['volume'] >= 10:
                day_trade_score += 5
                senior_warnings.append("Low volume - wait for momentum")
            else:
                senior_warnings.append("No volume today - avoid")
                continue  # Skip options with no volume
            
            # Spread analysis (critical for day trading)
            if data['bid'] > 0 and data['ask'] > 0:
                spread_pct = ((data['ask'] - data['bid']) / data['ask']) * 100
                if spread_pct <= 3:
                    day_trade_score += 25
                    senior_strengths.append(f"Excellent spread: {spread_pct:.1f}%")
                elif spread_pct <= 7:
                    day_trade_score += 15
                    senior_strengths.append(f"Good spread: {spread_pct:.1f}%")
                elif spread_pct <= 12:
                    day_trade_score += 5
                    senior_warnings.append(f"Wide spread: {spread_pct:.1f}%")
                else:
                    senior_warnings.append(f"Very wide spread: {spread_pct:.1f}% - avoid")
                    continue
            else:
                senior_warnings.append("No bid/ask - can't trade")
                continue
            
            # Price level analysis (avoid penny options for day trading)
            if data['last_trade'] >= 0.20:
                day_trade_score += 15
                senior_strengths.append("Good option price")
            elif data['last_trade'] >= 0.10:
                day_trade_score += 10
                senior_strengths.append("Acceptable option price")
            elif data['last_trade'] >= 0.05:
                day_trade_score += 5
                senior_warnings.append("Low option price")
            else:
                senior_warnings.append("Penny option - avoid for day trading")
                continue
            
            # Calculate final day trading score
            option['day_trade_score'] = day_trade_score
            option['senior_warnings'] = senior_warnings
            option['senior_strengths'] = senior_strengths
            
            # Only include if meets day trading standards
            if day_trade_score >= 40:  # Minimum threshold for day trading
                senior_filtered.append(option)
        
        # Sort by day trading score
        senior_filtered.sort(key=lambda x: x['day_trade_score'], reverse=True)
        
        # Update results
        results['tradeable_options'] = senior_filtered
        results['senior_filtered_count'] = len(senior_filtered)
        
        print(f"✅ Senior filter applied: {len(senior_filtered)} options suitable for day trading")
        
        return results
    
    def get_daily_tradeable_options(self, max_options: int = 10) -> List[Dict]:
        """
        Main method: Get today's best tradeable options for the robot
        
        Returns:
            List of dictionaries in robot-compatible format
        """
        print("🚀 GETTING DAILY TRADEABLE OPTIONS")
        print("=" * 80)
        
        # Step 1: Discover active options
        discovered = self.discover_active_options()
        if not discovered:
            print("❌ No active options discovered")
            return []
        
        # Step 2: Analyze and filter
        analyzed = self.analyze_and_filter_options(discovered)
        if not analyzed.get('tradeable_options'):
            print("❌ No tradeable options after analysis")
            return []
        
        # Step 3: Convert to robot format
        robot_options = []
        for option in analyzed['tradeable_options'][:max_options]:
            data = option['option_data']
            
            robot_option = {
                'symbol': data['symbol'],
                'underlying': data['underlying'],
                'score': option['quality_score'],
                'day_trade_score': option.get('day_trade_score', 0),
                'rating': option['overall_rating'],
                'liquidity_rating': option['liquidity_rating'],
                'open_interest': data['open_interest'],
                'volume': data['volume'],
                'bid': data['bid'],
                'ask': data['ask'],
                'last_trade': data['last_trade'],
                'spread_pct': ((data['ask'] - data['bid']) / data['ask'] * 100) if data['ask'] > 0 else 0,
                'type': data['type'],
                'strike': data['strike'],
                'expiry': data['expiry'],
                'discovery_timestamp': datetime.now().isoformat(),
                'strengths': option['strengths'] + option.get('senior_strengths', []),
                'warnings': option['warnings'] + option.get('senior_warnings', [])
            }
            
            robot_options.append(robot_option)
        
        # Step 4: Print summary for robot
        print(f"\n🎯 ROBOT-READY OPTIONS:")
        print(f"   Found {len(robot_options)} day-tradeable options")
        
        if robot_options:
            print("\n🏆 Top 5 recommendations:")
            for i, opt in enumerate(robot_options[:5]):
                print(f"   {i+1}. {opt['symbol']} ({opt['underlying']}) - Score: {opt['score']}/100")
                print(f"      Day Trade Score: {opt['day_trade_score']}/100 | Rating: {opt['rating']}")
                print(f"      OI: {opt['open_interest']:,} | Vol: {opt['volume']} | Spread: {opt['spread_pct']:.1f}%")
        
        # Step 5: Save results for debugging
        output_file = 'enhanced_tradeable_options.json'
        with open(output_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'total_discovered': sum(len(v['options']) for v in discovered.values()),
                'analyzed_results': analyzed,
                'robot_options': robot_options
            }, f, indent=2)
        
        print(f"\n💾 Detailed results saved to: {output_file}")
        
        return robot_options

def main():
    """Test the enhanced discovery system"""
    discovery = EnhancedOptionsDiscovery()
    options = discovery.get_daily_tradeable_options(max_options=15)
    
    if options:
        print(f"\n✅ SUCCESS: Found {len(options)} tradeable options for the robot!")
        print("🚀 Ready for integration with options_robot.py")
    else:
        print("\n⚠️ No tradeable options found today")
        print("   This could mean market is closed or low volatility")

if __name__ == "__main__":
    main()
