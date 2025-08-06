#!/usr/bin/env python3
"""
PRODUCTION Options Discovery - Final Integration Ready
Uses real CedroTech quotes endpoint with proper field mapping
Ready for integration with options_robot.py
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from cedrotech_options_api import CedroTechOptionsAPI
from options_filter_analysis import OptionsTradeabilityAnalyzer

class ProductionOptionsDiscovery:
    """
    PRODUCTION-READY options discovery with real CedroTech integration
    Uses actual API data structure discovered from debugging
    """
    
    def __init__(self):
        self.options_api = CedroTechOptionsAPI()
        self.analyzer = OptionsTradeabilityAnalyzer()
        
        # Major Ibovespa underlyings to check
        self.underlyings = [
            'VALE3', 'PETR4', 'ITUB4', 'BBAS3', 'B3SA3',  # Blue chips
            'ABEV3', 'MGLU3', 'WEGE3', 'RENT3', 'LREN3'   # Large caps
        ]
        
    def discover_real_options(self) -> Dict[str, List[Dict]]:
        """
        Discover REAL active options using production-ready endpoint mapping
        Returns only options with actual open interest and market activity
        """
        print("🚀 PRODUCTION OPTIONS DISCOVERY - USING REAL API DATA")
        print("=" * 70)
        
        if not self.options_api.authenticate():
            print("❌ Failed to authenticate with CedroTech API")
            return {}
        
        discovered_options = {}
        total_real_options = 0
        
        # Company name mapping for the API
        company_mapping = {
            'VALE3': 'VALE',
            'PETR4': 'PETROBRAS', 
            'ITUB4': 'ITAU',
            'BBAS3': 'BRADESCO',
            'B3SA3': 'B3',
            'ABEV3': 'AMBEV',
            'MGLU3': 'MAGALU',
            'WEGE3': 'WEG',
            'RENT3': 'LOCALIZA',
            'LREN3': 'LOJAS_RENNER'
        }
        
        for underlying in self.underlyings:
            company_name = company_mapping.get(underlying, underlying.replace('3', '').replace('4', ''))
            print(f"\n📊 Getting REAL options for {underlying} (company: {company_name})...")
            
            # Use the WORKING companyQuotes endpoint
            real_options = self._get_company_options(company_name, underlying)
            
            if real_options:
                discovered_options[underlying] = {'options': real_options}
                total_real_options += len(real_options)
                print(f"   ✅ Found {len(real_options)} REAL tradeable options for {underlying}")
                
                # Show sample of real options found
                for i, opt in enumerate(real_options[:3]):  # Show first 3
                    market_status = "ACTIVE" if opt.get('open_interest', 0) > 1000 else "LOW_OI"
                    print(f"      {i+1}. {opt['symbol']} - OI: {opt.get('open_interest', 0):,} ({market_status})")
            else:
                print(f"   ⚠️ No tradeable options found for {underlying}")
        
        print(f"\n🎯 DISCOVERY SUMMARY:")
        print(f"   Total REAL tradeable options found: {total_real_options}")
        print(f"   Underlyings with options: {len(discovered_options)}")
        
        return discovered_options
    
    def _get_company_options(self, company_name: str, underlying: str) -> List[Dict]:
        """Get options for a company using the working companyQuotes endpoint"""
        try:
            # Use the session from authenticated API
            session = self.options_api.session
            base_url = self.options_api.base_url
            
            # Company quotes endpoint - this WORKS!
            company_url = f"{base_url}/services/quotes/companyQuotes"
            params = {
                "company": company_name,
                "types": "2",  # Options type
                "markets": "1"  # Bovespa market
            }
            headers = {"accept": "application/json"}
            
            response = session.get(company_url, headers=headers, params=params)
            
            if response.status_code == 200:
                try:
                    options_symbols = response.json()
                    
                    if isinstance(options_symbols, list) and options_symbols:
                        print(f"   📋 Found {len(options_symbols)} option symbols from API")
                        
                        # Get quotes for each option (limit to top 40 for performance)
                        real_options = []
                        for i, symbol in enumerate(options_symbols[:40]):  # Process top 40 options
                            option_data = self._get_production_option_data(symbol, underlying)
                            if option_data:
                                real_options.append(option_data)
                            
                            # Show progress every 15 options
                            if (i + 1) % 15 == 0:
                                print(f"      📊 Processed {i + 1}/{min(40, len(options_symbols))} options...")
                        
                        print(f"   💰 Successfully got data for {len(real_options)} options")
                        return real_options
                    else:
                        print(f"   ⚠️ No options returned in list format")
                        return []
                        
                except json.JSONDecodeError:
                    print(f"   ❌ Invalid JSON response")
                    return []
            else:
                print(f"   ❌ Company quotes failed: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"   💥 Error getting company options: {e}")
            return []
    
    def _get_production_option_data(self, symbol: str, underlying: str) -> Optional[Dict]:
        """Get production-ready option data using real API field mapping"""
        try:
            # Use the quotes endpoint for real-time data
            result = self.options_api.get_option_quote(symbol)
            
            if result.get('success'):
                data = result.get('data', {})
                
                # Map real API fields to our format (based on debug discovery)
                bid = float(data.get('bid', 0) or 0)
                ask = float(data.get('ask', 0) or 0)
                last_trade = float(data.get('lastTrade', 0) or 0)
                volume = int(data.get('volumeAmount', 0) or 0)  # Real field name from API
                open_interest = int(data.get('interest', 0) or 0)  # Real field name from API
                
                # Additional real fields from the API
                company = data.get('company', '')
                option_type = data.get('typeOption', '')  # A = American
                direction = data.get('directionOption', '')  # C = Call, P = Put
                parent_symbol = data.get('parentSymbol', '')
                security_type = data.get('securityType', '')
                contract_multiplier = float(data.get('contractMultiplier', 1) or 1)
                
                # Market update info
                time_update = data.get('timeUpdate', '')
                date_update = data.get('dateUpdate', '')
                
                # Check if option has meaningful activity (open interest is key indicator)
                has_activity = (
                    open_interest > 0 or  # Has open contracts
                    bid > 0 or ask > 0 or  # Has quotes (during market hours)
                    last_trade > 0 or  # Has traded
                    volume > 0  # Has volume
                )
                
                if has_activity:
                    return {
                        'symbol': symbol,
                        'underlying': underlying,
                        'bid': bid,
                        'ask': ask,
                        'last_trade': last_trade,
                        'volume': volume,
                        'open_interest': open_interest,
                        
                        # Enhanced data from real API
                        'company': company,
                        'option_type': option_type,
                        'direction': direction,
                        'parent_symbol': parent_symbol,
                        'security_type': security_type,
                        'contract_multiplier': contract_multiplier,
                        'time_update': time_update,
                        'date_update': date_update,
                        
                        # Metadata
                        'discovery_time': datetime.now().isoformat(),
                        'raw_data': data,
                        'has_real_data': True,
                        'api_source': 'cedrotech_quotes'
                    }
            
            return None
            
        except Exception as e:
            return None
    
    def get_daily_tradeable_options(self, max_options: int = 15) -> List[Dict]:
        """
        MAIN METHOD: Get today's REAL tradeable options for the robot
        
        Returns:
            List of validated, real options in robot-compatible format
        """
        print("🚀 PRODUCTION: GETTING DAILY TRADEABLE OPTIONS FOR ROBOT")
        print("=" * 80)
        
        # Step 1: Discover real options from API
        discovered = self.discover_real_options()
        if not discovered:
            print("❌ No real options discovered from API")
            return []
        
        # Step 2: Apply quality analysis
        print("\n📊 APPLYING QUALITY ANALYSIS...")
        analyzed = self.analyzer.filter_tradeable_options(discovered)
        
        if not analyzed.get('tradeable_options'):
            print("❌ No tradeable options after quality analysis")
            return []
        
        # Step 3: Convert to robot format with enhanced data
        robot_options = []
        for option in analyzed['tradeable_options'][:max_options]:
            data = option['option_data']
            
            robot_option = {
                # Core robot fields
                'symbol': data['symbol'],
                'underlying': data['underlying'],
                'score': option['quality_score'],
                'rating': option['overall_rating'],
                'liquidity_rating': option['liquidity_rating'],
                'open_interest': data['open_interest'],
                'volume': data['volume'],
                'bid': data['bid'],
                'ask': data['ask'],
                'last_trade': data['last_trade'],
                'spread_pct': ((data['ask'] - data['bid']) / data['ask'] * 100) if data['ask'] > 0 else 0,
                
                # Enhanced fields from real API
                'option_type': data.get('option_type', ''),
                'direction': data.get('direction', ''),
                'company': data.get('company', ''),
                'contract_multiplier': data.get('contract_multiplier', 1),
                'time_update': data.get('time_update', ''),
                
                # Metadata
                'discovery_timestamp': datetime.now().isoformat(),
                'strengths': option['strengths'],
                'warnings': option['warnings'],
                'is_real_option': True,
                'has_real_data': data.get('has_real_data', False),
                'discovery_method': 'production_cedrotech_api'
            }
            
            robot_options.append(robot_option)
        
        # Step 4: Print production summary
        print(f"\n🎯 PRODUCTION OPTIONS READY FOR ROBOT:")
        print(f"   Found {len(robot_options)} REAL tradeable options")
        
        if robot_options:
            print("\n🏆 Top 5 production options:")
            for i, opt in enumerate(robot_options[:5]):
                # Check if we have live quotes or just open interest
                quote_status = "LIVE QUOTES" if (opt['bid'] > 0 or opt['ask'] > 0) else "MARKET CLOSED"
                oi_status = "HIGH OI" if opt['open_interest'] > 10000 else "MEDIUM OI" if opt['open_interest'] > 1000 else "LOW OI"
                
                print(f"   {i+1}. {opt['symbol']} ({opt['underlying']}) - Score: {opt['score']}/100")
                print(f"      OI: {opt['open_interest']:,} ({oi_status}) | {quote_status} | Type: {opt.get('direction', 'N/A')}")
        
        # Step 5: Save production results
        with open('production_options_discovery.json', 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'discovery_method': 'production_cedrotech_api',
                'market_status': 'Real-time CedroTech API integration',
                'discovered_count': sum(len(v['options']) for v in discovered.values()),
                'robot_options': robot_options,
                'api_fields_mapped': [
                    'bid', 'ask', 'lastTrade', 'volumeAmount', 'interest',
                    'company', 'typeOption', 'directionOption', 'contractMultiplier'
                ]
            }, f, indent=2)
        
        print(f"\n💾 Production results saved to: production_options_discovery.json")
        
        return robot_options

def main():
    """Test the PRODUCTION discovery system"""
    print("🚀 PRODUCTION OPTIONS DISCOVERY TEST")
    print("=" * 80)
    
    discovery = ProductionOptionsDiscovery()
    options = discovery.get_daily_tradeable_options(max_options=20)
    
    if options:
        print(f"\n✅ PRODUCTION SUCCESS: Found {len(options)} REAL tradeable options!")
        print("🏆 Ready for LIVE integration with options_robot.py")
        
        # Production analysis
        total_oi = sum(opt['open_interest'] for opt in options)
        with_quotes = sum(1 for opt in options if opt['bid'] > 0 or opt['ask'] > 0)
        high_oi = sum(1 for opt in options if opt['open_interest'] > 10000)
        
        print(f"\n📊 Production Statistics:")
        print(f"   Total Open Interest: {total_oi:,} contracts")
        print(f"   Options with live quotes: {with_quotes}/{len(options)}")
        print(f"   High OI options (>10k): {high_oi}/{len(options)}")
        
        # Breakdown by underlying
        by_underlying = {}
        for opt in options:
            underlying = opt['underlying']
            if underlying not in by_underlying:
                by_underlying[underlying] = []
            by_underlying[underlying].append(opt)
        
        print(f"\n🎯 Options by underlying:")
        for underlying, opts in by_underlying.items():
            total_oi_underlying = sum(opt['open_interest'] for opt in opts)
            print(f"   {underlying}: {len(opts)} options, OI: {total_oi_underlying:,}")
        
        print(f"\n🚀 INTEGRATION STATUS: READY FOR PRODUCTION")
        print("   ✅ Real API data discovered and mapped")
        print("   ✅ Quality analysis applied")
        print("   ✅ Robot-compatible format generated")
        print("   ✅ Can replace hardcoded options in robot")
        
    else:
        print("\n⚠️ No options found - but this is expected if:")
        print("   - Market is closed (normal for evenings/weekends)")
        print("   - All options filtered out by quality analysis")
        print("   - Testing during non-market hours")
        print("\n💡 During market hours (9:00-17:30 BRT), you should see live quotes!")

if __name__ == "__main__":
    main()
