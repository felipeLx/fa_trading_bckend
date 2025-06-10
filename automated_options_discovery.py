#!/usr/bin/env python3
"""
Automated Options Discovery and Analysis
Comprehensive system to discover and analyze options for trading integration
"""

import requests
import json
from typing import Dict, List, Optional
import time
import os
from dotenv import load_dotenv
load_dotenv()

class CedroTechOptionsDiscovery:
    """Automated options discovery and analysis system"""
    
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.base_url = "https://webfeeder.cedrotech.com"
        self.session = requests.Session()
        self.authenticated = False
        
    def authenticate(self) -> bool:
        """Authenticate with CedroTech API"""
        print("🔐 Authenticating with CedroTech...")
        
        auth_url = f"{self.base_url}/SignIn"
        auth_params = {
            "login": self.username,
            "password": self.password
        }
        auth_headers = {"accept": "application/json"}
        
        response = self.session.post(auth_url, headers=auth_headers, params=auth_params)
        
        if response.status_code == 200:
            print("   ✅ Authentication successful!")
            self.authenticated = True
            return True
        else:
            print(f"   ❌ Authentication failed: {response.status_code}")
            return False
    
    def get_company_options(self, company: str) -> List[str]:
        """Get all options symbols for a specific company"""
        if not self.authenticated:
            print("❌ Not authenticated!")
            return []
        
        print(f"📊 Getting options for {company}...")
        
        # Company quotes endpoint for options
        company_url = f"{self.base_url}/services/quotes/companyQuotes"
        params = {
            "company": company,
            "types": "2",  # Options
            "markets": "1"  # Bovespa
        }
        headers = {"accept": "application/json"}
        
        response = self.session.get(company_url, headers=headers, params=params)
        
        if response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, list):
                    print(f"   ✅ Found {len(data)} options for {company}")
                    return data
                else:
                    print(f"   ⚠️  Unexpected response format: {type(data)}")
                    return []
            except json.JSONDecodeError:
                print(f"   ❌ Failed to parse JSON response")
                return []
        else:
            print(f"   ❌ Failed to get options: {response.status_code}")
            return []
    
    def get_option_details(self, symbol: str) -> Optional[Dict]:
        """Get detailed information for a specific option symbol"""
        if not self.authenticated:
            return None
        
        # Use regular quote endpoint for individual option
        quote_url = f"{self.base_url}/services/quotes/quote/{symbol}"
        headers = {"accept": "application/json"}
        
        response = self.session.get(quote_url, headers=headers)
        
        if response.status_code == 200:
            try:
                return response.json()
            except json.JSONDecodeError:
                return None
        return None
    
    def analyze_option(self, option_data: Dict) -> Dict:
        """Analyze option data and extract key trading information"""
        
        # Helper function to safely convert to float
        def safe_float(value, default=0.0):
            try:
                if value is None or value == '':
                    return default
                return float(value)
            except (ValueError, TypeError):
                return default
        
        # Helper function to safely convert to int
        def safe_int(value, default=0):
            try:
                if value is None or value == '':
                    return default
                return int(float(value))  # Convert through float first to handle string decimals
            except (ValueError, TypeError):
                return default
        
        analysis = {
            'symbol': option_data.get('symbol', 'N/A'),
            'underlying': option_data.get('parentSymbol', 'N/A'),
            'type': option_data.get('typeOption', 'N/A'),
            'direction': option_data.get('directionOption', 'N/A'),
            'last_trade': safe_float(option_data.get('lastTrade', 0)),
            'bid': safe_float(option_data.get('bid', 0)),
            'ask': safe_float(option_data.get('ask', 0)),
            'theory_price': safe_float(option_data.get('theoryPrice', 0)),
            'volume': safe_int(option_data.get('volumeAmount', 0)),
            'open_interest': safe_int(option_data.get('interest', 0)),
            'contract_multiplier': safe_int(option_data.get('contractMultiplier', 1)),
            'change': safe_float(option_data.get('change', 0)),
            'change_percent': safe_float(option_data.get('changeWeek', 0)),
            'high': safe_float(option_data.get('high', 0)),
            'low': safe_float(option_data.get('low', 0)),
            'market_cap': safe_float(option_data.get('marketCap', 0))
        }
        
        # Calculate spread
        if analysis['bid'] > 0 and analysis['ask'] > 0:
            analysis['spread'] = analysis['ask'] - analysis['bid']
            analysis['spread_percent'] = (analysis['spread'] / analysis['ask']) * 100 if analysis['ask'] > 0 else 0
        else:
            analysis['spread'] = 0
            analysis['spread_percent'] = 0
        
        # Determine if option is liquid (has meaningful bid/ask)
        analysis['is_liquid'] = analysis['bid'] > 0 and analysis['ask'] > 0 and analysis['volume'] > 0
        
        # Calculate moneyness indicator (simplified)
        analysis['has_value'] = analysis['last_trade'] > 0 or analysis['theory_price'] > 0
        
        return analysis
    
    def discover_and_analyze_options(self, companies: List[str], max_options_per_company: int = 50) -> Dict:
        """Discover and analyze options for multiple companies"""
        print("🚀 Starting Automated Options Discovery...")
        print("=" * 60)
        
        if not self.authenticate():
            return {}
        
        all_results = {}
        
        for company in companies:
            print(f"\n🏢 Processing {company}...")
            
            # Get option symbols for this company
            option_symbols = self.get_company_options(company)
            
            if not option_symbols:
                print(f"   ⚠️  No options found for {company}")
                continue
            
            # Limit options to analyze (avoid overwhelming the API)
            symbols_to_analyze = option_symbols[:max_options_per_company]
            
            company_results = {
                'total_options': len(option_symbols),
                'analyzed_options': len(symbols_to_analyze),
                'options': [],
                'summary': {
                    'liquid_options': 0,
                    'call_options': 0,
                    'put_options': 0,
                    'avg_spread': 0,
                    'total_volume': 0
                }
            }
            
            print(f"   📊 Analyzing {len(symbols_to_analyze)} options...")
            
            for i, symbol in enumerate(symbols_to_analyze):
                # Rate limiting - don't overwhelm the API
                if i > 0 and i % 10 == 0:
                    print(f"   🔄 Processed {i} options...")
                    time.sleep(0.5)  # Brief pause
                
                option_details = self.get_option_details(symbol)
                
                if option_details:
                    analysis = self.analyze_option(option_details)
                    company_results['options'].append(analysis)
                    
                    # Update summary statistics
                    summary = company_results['summary']
                    if analysis['is_liquid']:
                        summary['liquid_options'] += 1
                    
                    if analysis['direction'] and 'call' in analysis['direction'].lower():
                        summary['call_options'] += 1
                    elif analysis['direction'] and 'put' in analysis['direction'].lower():
                        summary['put_options'] += 1
                    
                    summary['total_volume'] += analysis['volume']
                    
                    if analysis['spread'] > 0:
                        summary['avg_spread'] += analysis['spread']
            
            # Calculate average spread
            liquid_count = company_results['summary']['liquid_options']
            if liquid_count > 0:
                company_results['summary']['avg_spread'] /= liquid_count
            
            all_results[company] = company_results
            
            print(f"   ✅ Completed {company}: {liquid_count} liquid options found")
        
        return all_results
    
    def print_results_summary(self, results: Dict):
        """Print a comprehensive summary of the options analysis"""
        print(f"\n\n📈 OPTIONS DISCOVERY RESULTS")
        print("=" * 60)
        
        total_companies = len(results)
        total_options = sum(r['total_options'] for r in results.values())
        total_liquid = sum(r['summary']['liquid_options'] for r in results.values())
        
        print(f"🏢 Companies analyzed: {total_companies}")
        print(f"📊 Total options found: {total_options}")
        print(f"💧 Liquid options: {total_liquid}")
        print(f"📈 Liquidity rate: {(total_liquid/total_options*100):.1f}%" if total_options > 0 else "📈 Liquidity rate: 0%")
        
        print(f"\n📋 Company Breakdown:")
        print("-" * 40)
        
        for company, data in results.items():
            summary = data['summary']
            print(f"{company}:")
            print(f"  📊 Total: {data['total_options']} options")
            print(f"  💧 Liquid: {summary['liquid_options']} options")
            print(f"  📈 Calls: {summary['call_options']}")
            print(f"  📉 Puts: {summary['put_options']}")
            print(f"  💰 Avg Spread: R$ {summary['avg_spread']:.4f}")
            print(f"  📦 Total Volume: {summary['total_volume']}")
            
            # Show top 3 most liquid options
            liquid_options = [opt for opt in data['options'] if opt['is_liquid']]
            if liquid_options:
                # Sort by volume
                liquid_options.sort(key=lambda x: x['volume'], reverse=True)
                print(f"  🎯 Top liquid options:")
                for opt in liquid_options[:3]:
                    print(f"    • {opt['symbol']}: Vol={opt['volume']}, Spread=R${opt['spread']:.4f}")
            print()
        
        print(f"\n💡 Integration Recommendations:")
        print("-" * 40)
        
        if total_liquid > 0:
            print("✅ OPTIONS INTEGRATION IS VIABLE!")
            print("🎯 Recommended next steps:")
            print("  1. Focus on liquid options with tight spreads")
            print("  2. Implement options-specific risk management")
            print("  3. Add options analysis to trading robot")
            print("  4. Start with VALE options (most liquid)")
        else:
            print("⚠️  Limited liquid options found")
            print("🎯 Consider:")
            print("  1. Using options for hedging only")
            print("  2. Focusing on high-volume periods")
            print("  3. Manual options selection")

def main():
    """Main function to run automated options discovery"""
    # Platform credentials that work
    username = os.getenv("CEDROTECH_PLATFORM", "")
    password = os.getenv("CEDROTECH_PLAT_PASSWORD", "")
    
    # Companies to analyze
    companies = ["VALE", "PETROBRAS", "BRADESCO", "ITAU", "AMBEV"]
    
    # Initialize discovery system
    options_discovery = CedroTechOptionsDiscovery(username, password)
    
    # Run comprehensive analysis
    results = options_discovery.discover_and_analyze_options(companies, max_options_per_company=30)
    
    # Print results
    options_discovery.print_results_summary(results)
    
    # Save results to file for later use
    with open('options_discovery_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to 'options_discovery_results.json'")
    print(f"🎯 Ready for options trading integration!")

if __name__ == "__main__":
    main()
