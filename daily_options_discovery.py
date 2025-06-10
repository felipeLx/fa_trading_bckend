#!/usr/bin/env python3
"""
Daily Options Discovery for Options Robot
Simplified runner that discovers and analyzes options for daily trading
"""

import json
import os
from datetime import datetime
from cedrotech_options_api import CedroTechOptionsAPI
from options_filter_analysis import OptionsTradeabilityAnalyzer

def discover_and_analyze_daily_options():
    """
    Discover options and run analysis to find today's best tradeable options
    
    Returns:
        dict: Analysis results with tradeable options
    """
    print("🔍 DAILY OPTIONS DISCOVERY & ANALYSIS")
    print("=" * 50)
    
    try:
        # Initialize APIs
        print("📡 Initializing CedroTech Options API...")
        options_api = CedroTechOptionsAPI()
        
        if not options_api.authenticate():
            print("❌ Failed to authenticate with CedroTech API")
            return None
        
        # Discover options for major underlyings
        underlyings = ['VALE3', 'PETR4', 'ITUB4', 'BBAS3', 'B3SA3']
        all_options = {}
        
        print(f"\n🎯 Discovering options for {len(underlyings)} underlyings...")
        for underlying in underlyings:
            print(f"   📊 Searching {underlying} options...")
            
            options_result = options_api.get_options_list(underlying)
            if options_result.get('success') and options_result.get('options'):
                options_data = options_result['options']
                all_options[underlying] = options_data
                print(f"      ✅ Found {len(options_data)} {underlying} options")
            else:
                print(f"      ⚠️ No options found for {underlying}")
        
        if not all_options:
            print("❌ No options discovered")
            return None
        
        # Save discovery results
        discovery_file = 'options_discovery_results.json'
        with open(discovery_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'discovered_options': all_options
            }, f, indent=2)
        
        print(f"💾 Options discovery saved to {discovery_file}")
        
        # Run tradeability analysis
        print("\n🎯 Running tradeability analysis...")
        analyzer = OptionsTradeabilityAnalyzer()
        
        # Flatten all options for analysis
        flat_options = []
        for underlying, options in all_options.items():
            for option in options:
                option['underlying'] = underlying
                flat_options.append(option)
        
        # Create analysis input format
        analysis_input = {
            'options': flat_options,
            'timestamp': datetime.now().isoformat()
        }
        
        # Run analysis
        filtered_results = analyzer.filter_tradeable_options(analysis_input)
        
        # Save analysis results
        analysis_file = 'tradeable_options_analysis.json'
        with open(analysis_file, 'w') as f:
            json.dump(filtered_results, f, indent=2)
        
        print(f"💾 Analysis results saved to {analysis_file}")
        
        # Print summary
        analyzer.print_trading_recommendations(filtered_results)
        
        return filtered_results
        
    except Exception as e:
        print(f"❌ Error in daily options discovery: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    results = discover_and_analyze_daily_options()
    
    if results and results.get('tradeable_options'):
        print(f"\n🎉 SUCCESS: Found {len(results['tradeable_options'])} tradeable options")
        print("🚀 Ready for options trading robot!")
    else:
        print("\n⚠️ No tradeable options found today")
