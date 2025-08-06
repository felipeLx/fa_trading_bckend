"""
Comprehensive CedroTech Market API Endpoint Tester
Tests all available endpoints with VALE3 as the primary ticker
Helps identify working endpoints and data structures
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv
load_dotenv()

class CedroTechAPITester:
    """
    Complete tester for all CedroTech Market API endpoints with proper authentication
    """
    
    def __init__(self):
        self.base_url = "https://webfeeder.cedrotech.com"
        self.session = requests.Session()
        self.results = {}
        self.test_ticker = "VALE3"
        self.authenticated = False
        
        # Get credentials from environment
        self.platform_user = os.getenv('CEDROTECH_PLATAFORM')
        self.platform_password = os.getenv('CEDROTECH_PLAT_PASSWORD')
        
        # Set up session headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Connection': 'keep-alive'
        })
        
        # Get date ranges for news endpoints
        today = datetime.now()
        week_ago = today - timedelta(days=7)
        self.date_from = week_ago.strftime("%d%m%Y")
        self.date_to = today.strftime("%d%m%Y")
    
    def authenticate(self):
        """
        Authenticate with CedroTech platform to get session cookies
        """
        print("🔐 AUTHENTICATING WITH CEDROTECH API...")
        print(f"   User: {self.platform_user}")
        
        if not self.platform_user or not self.platform_password:
            print("❌ Missing credentials! Check CEDROTECH_PLATAFORM and CEDROTECH_PLAT_PASSWORD environment variables")
            return False
        
        try:
            # Authentication endpoint
            auth_url = f"{self.base_url}/SignIn"
            
            # Authentication parameters
            params = {
                "login": self.platform_user,
                "password": self.platform_password
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
                    print(f"   ✅ Authentication successful!")
                    print(f"   🍪 Session cookies: {list(cookies.keys())}")
                    self.authenticated = True
                    return True
                else:
                    print(f"   ⚠️ No session cookies received")
                    print(f"   Response: {response.text[:200]}")
                    return False
            else:
                print(f"   ❌ Authentication failed: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return False
                
        except Exception as e:
            print(f"   💥 Authentication error: {e}")
            return False
        
    def test_endpoint(self, name: str, url: str, description: str, expected_status: int = 200) -> Dict[str, Any]:
        """
        Test a single endpoint and return comprehensive results
        """
        print(f"\n🔍 Testing: {name}")
        print(f"📋 Description: {description}")
        print(f"🌐 URL: {url}")
        
        try:
            start_time = time.time()
            response = self.session.get(url, timeout=10)
            response_time = time.time() - start_time
            
            result = {
                'name': name,
                'description': description,
                'url': url,
                'status_code': response.status_code,
                'response_time_ms': round(response_time * 1000, 2),
                'success': response.status_code == expected_status,
                'timestamp': datetime.now().isoformat(),
                'headers': dict(response.headers),
                'data_size_bytes': len(response.content)
            }
            
            # Try to parse JSON response
            try:
                json_data = response.json()
                result['has_json'] = True
                result['data'] = json_data
                result['data_type'] = type(json_data).__name__
                
                # Analyze data structure
                if isinstance(json_data, list):
                    result['data_count'] = len(json_data)
                    result['sample_item'] = json_data[0] if json_data else None
                elif isinstance(json_data, dict):
                    result['data_keys'] = list(json_data.keys())
                    result['data_count'] = len(json_data)
                
                print(f"   ✅ Status: {response.status_code} | Time: {result['response_time_ms']}ms")
                print(f"   📊 Data: {result['data_type']} | Size: {result['data_size_bytes']} bytes")
                
                if result.get('data_count'):
                    print(f"   📈 Count: {result['data_count']} items")
                
            except json.JSONDecodeError:
                result['has_json'] = False
                result['raw_text'] = response.text[:500]  # First 500 chars
                print(f"   ⚠️ Status: {response.status_code} | Non-JSON response")
                
        except requests.exceptions.Timeout:
            result = {
                'name': name,
                'description': description,
                'url': url,
                'success': False,
                'error': 'Request timeout (10s)',
                'timestamp': datetime.now().isoformat()
            }
            print(f"   ❌ Timeout after 10 seconds")
            
        except requests.exceptions.RequestException as e:
            result = {
                'name': name,
                'description': description,
                'url': url,
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            print(f"   ❌ Request error: {str(e)[:100]}")
        
        return result
    
    def test_all_endpoints(self):
        """
        Test all CedroTech API endpoints systematically with authentication
        """
        print("🚀 COMPREHENSIVE CEDROTECH API ENDPOINT TESTING")
        print("=" * 80)
        print(f"📊 Test Ticker: {self.test_ticker}")
        print(f"📅 Date Range: {self.date_from} to {self.date_to}")
        print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # STEP 1: Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed - cannot test endpoints")
            return
        
        print(f"\n✅ Authentication successful - proceeding with endpoint testing...")
        
        # Define all endpoints to test
        endpoints = [
            # QUOTES ENDPOINTS
            {
                'name': 'quote_asset',
                'url': f"{self.base_url}/services/quotes/quote/{self.test_ticker}",
                'description': 'Consultar cotação de ativo'
            },
            {
                'name': 'high_list',
                'url': f"{self.base_url}/services/quotes/highList/IBOV",
                'description': 'Consultar maiores altas do índice'
            },
            {
                'name': 'fall_list',
                'url': f"{self.base_url}/services/quotes/fallList/IBOV",
                'description': 'Consultar maiores baixas do índice'
            },
            {
                'name': 'list_market',
                'url': f"{self.base_url}/services/quotes/listMarket",
                'description': 'Consultar lista de mercados'
            },
            {
                'name': 'company_quotes',
                'url': f"{self.base_url}/services/quotes/companyQuotes?company={self.test_ticker}&types=2&markets=1",
                'description': 'Consultar lista de papéis da empresa (options)'
            },
            {
                'name': 'quotes_index',
                'url': f"{self.base_url}/services/quotes/quotesIndex/BOVESPA/IBOV",
                'description': 'Consultar lista de ativos de um índice'
            },
            {
                'name': 'options_quote',
                'url': f"{self.base_url}/services/quotes/optionsQuote/{self.test_ticker}",
                'description': 'Consultar lista de opções de um ativo'
            },
            {
                'name': 'index_list',
                'url': f"{self.base_url}/services/quotes/indexList?marketcode=1",
                'description': 'Consultar lista de índices de um mercado'
            },
            {
                'name': 'quote_information',
                'url': f"{self.base_url}/services/quotes/quoteInformation?description={self.test_ticker}",
                'description': 'Consultar informações de um ativo'
            },
            {
                'name': 'book',
                'url': f"{self.base_url}/services/quotes/book/{self.test_ticker}",
                'description': 'Consultar livro de ofertas'
            },
            {
                'name': 'mini_book',
                'url': f"{self.base_url}/services/quotes/miniBook/{self.test_ticker}",
                'description': 'Consultar melhores ofertas do livro de ofertas'
            },
            {
                'name': 'aggregated_book',
                'url': f"{self.base_url}/services/quotes/aggregatedBook/{self.test_ticker}",
                'description': 'Consultar livro de ofertas agregado'
            },
            
            # NEWS ENDPOINTS
            {
                'name': 'news_by_date',
                'url': f"{self.base_url}/services/news/newsByDate/{self.date_from}/{self.date_to}",
                'description': 'Consultar notícias por período'
            },
            {
                'name': 'news_by_code',
                'url': f"{self.base_url}/services/news/newsByCode/1070292",
                'description': 'Consultar notícias por código'
            },
            {
                'name': 'relevant_facts',
                'url': f"{self.base_url}/services/news/newsRelevantFacts/{self.date_from}/{self.date_to}",
                'description': 'Consultar fatos relevantes por período'
            },
            {
                'name': 'relevant_facts_by_quote',
                'url': f"{self.base_url}/services/news/newsRelevantFactsByQuote/{self.date_from}/{self.date_to}/{self.test_ticker}",
                'description': 'Consultar fatos relevantes de um ativo por período'
            }
        ]
        
        # Test each endpoint
        for i, endpoint in enumerate(endpoints, 1):
            print(f"\n[{i}/{len(endpoints)}] " + "="*50)
            result = self.test_endpoint(
                endpoint['name'],
                endpoint['url'],
                endpoint['description']
            )
            self.results[endpoint['name']] = result
            
            # Small delay between requests to be respectful
            time.sleep(0.5)
        
        self._generate_summary()
        self._save_results()
    
    def _generate_summary(self):
        """
        Generate a comprehensive summary of all test results
        """
        print(f"\n" + "="*80)
        print("📊 CEDROTECH API TESTING SUMMARY")
        print("="*80)
        
        successful = [r for r in self.results.values() if r.get('success', False)]
        failed = [r for r in self.results.values() if not r.get('success', False)]
        
        print(f"✅ Successful endpoints: {len(successful)}/{len(self.results)}")
        print(f"❌ Failed endpoints: {len(failed)}/{len(self.results)}")
        
        if successful:
            print(f"\n🎯 WORKING ENDPOINTS:")
            for result in successful:
                status_info = f"({result['status_code']}, {result['response_time_ms']}ms)"
                data_info = ""
                if result.get('data_count'):
                    data_info = f" - {result['data_count']} items"
                elif result.get('data_type'):
                    data_info = f" - {result['data_type']}"
                
                print(f"   ✅ {result['name']}: {result['description']} {status_info}{data_info}")
        
        if failed:
            print(f"\n⚠️ FAILED ENDPOINTS:")
            for result in failed:
                error_info = result.get('error', f"Status {result.get('status_code', 'Unknown')}")
                print(f"   ❌ {result['name']}: {error_info}")
        
        # Analyze data richness
        print(f"\n📈 DATA ANALYSIS:")
        
        # Find endpoints with most data
        data_rich = [(r['name'], r.get('data_count', 0)) for r in successful if r.get('data_count', 0) > 0]
        data_rich.sort(key=lambda x: x[1], reverse=True)
        
        if data_rich:
            print(f"   🏆 Most data-rich endpoints:")
            for name, count in data_rich[:5]:
                print(f"      {name}: {count} items")
        
        # Find fastest endpoints
        fast_endpoints = [(r['name'], r['response_time_ms']) for r in successful if 'response_time_ms' in r]
        fast_endpoints.sort(key=lambda x: x[1])
        
        if fast_endpoints:
            print(f"   ⚡ Fastest endpoints:")
            for name, time_ms in fast_endpoints[:3]:
                print(f"      {name}: {time_ms}ms")
        
        # Check for options-related endpoints
        options_endpoints = [r for r in successful if 'option' in r['name'].lower()]
        if options_endpoints:
            print(f"\n🎯 OPTIONS-RELATED ENDPOINTS ({len(options_endpoints)} working):")
            for result in options_endpoints:
                count_info = f" ({result.get('data_count', 'unknown')} items)" if result.get('data_count') else ""
                print(f"   🔹 {result['name']}: {result['description']}{count_info}")
    
    def _save_results(self):
        """
        Save detailed results to JSON file
        """
        filename = f"cedrotech_api_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        output = {
            'test_metadata': {
                'test_ticker': self.test_ticker,
                'test_date': datetime.now().isoformat(),
                'date_range': f"{self.date_from} to {self.date_to}",
                'total_endpoints': len(self.results),
                'successful_endpoints': len([r for r in self.results.values() if r.get('success', False)]),
                'base_url': self.base_url
            },
            'results': self.results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Detailed results saved to: {filename}")
        
        # Also create a simplified CSV summary
        csv_filename = f"cedrotech_api_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(csv_filename, 'w', encoding='utf-8') as f:
            f.write("Endpoint,Description,Success,Status_Code,Response_Time_ms,Data_Count,Error\n")
            for result in self.results.values():
                f.write(f"{result['name']},{result['description']},{result.get('success', False)},")
                f.write(f"{result.get('status_code', '')},{result.get('response_time_ms', '')},")
                f.write(f"{result.get('data_count', '')},{result.get('error', '')}\n")
        
        print(f"📊 CSV summary saved to: {csv_filename}")
      
    def test_specific_endpoint(self, endpoint_name: str):
        """
        Test a specific endpoint by name for detailed analysis with authentication
        """
        # Authenticate first if not already done
        if not self.authenticated:
            print("🔐 Authenticating before testing specific endpoint...")
            if not self.authenticate():
                print("❌ Authentication failed - cannot test endpoint")
                return None
        
        endpoints_map = {
            'quote': f"{self.base_url}/services/quotes/quote/{self.test_ticker}",
            'company_quotes': f"{self.base_url}/services/quotes/companyQuotes?company={self.test_ticker}&types=2&markets=1",
            'options_quote': f"{self.base_url}/services/quotes/optionsQuote/{self.test_ticker}",
            'quote_information': f"{self.base_url}/services/quotes/quoteInformation?description={self.test_ticker}",
            'book': f"{self.base_url}/services/quotes/book/{self.test_ticker}"
        }
        
        if endpoint_name in endpoints_map:
            url = endpoints_map[endpoint_name]
            result = self.test_endpoint(endpoint_name, url, f"Detailed test of {endpoint_name}")
            
            if result.get('success') and result.get('data'):
                print(f"\n🔍 DETAILED DATA ANALYSIS FOR {endpoint_name.upper()}:")
                print("="*60)
                data = result['data']
                
                if isinstance(data, dict):
                    print("📋 Available fields:")
                    for key, value in data.items():
                        value_type = type(value).__name__
                        value_preview = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                        print(f"   {key}: {value_preview} ({value_type})")
                
                elif isinstance(data, list) and data:
                    print(f"📋 Array with {len(data)} items")
                    print("Sample item fields:")
                    sample = data[0]
                    if isinstance(sample, dict):
                        for key, value in sample.items():
                            value_type = type(value).__name__
                            print(f"   {key}: ({value_type})")
            
            return result
        else:
            print(f"❌ Unknown endpoint: {endpoint_name}")
            print(f"Available: {', '.join(endpoints_map.keys())}")
            return None

def main():
    """
    Main function to run comprehensive API testing with authentication
    """
    print("🚀 CEDROTECH MARKET API COMPREHENSIVE TESTER")
    print("=" * 80)
    print("This script will test all CedroTech API endpoints systematically")
    print("Testing with VALE3 as the primary ticker")
    print("IMPORTANT: Authentication will be performed first")
    print("=" * 80)
    
    tester = CedroTechAPITester()
    
    # Check credentials first
    if not tester.platform_user or not tester.platform_password:
        print("❌ MISSING CREDENTIALS!")
        print("Please ensure you have the following environment variables set:")
        print("   CEDROTECH_PLATAFORM=your_username")
        print("   CEDROTECH_PLAT_PASSWORD=your_password")
        print("\nYou can set them in a .env file or as system environment variables")
        return
    
    # Run comprehensive test with authentication
    tester.test_all_endpoints()
    
    print(f"\n🎯 TESTING COMPLETED!")
    print("Check the generated JSON and CSV files for detailed results")
    print("Use the results to identify the best endpoints for your trading system")

def test_single_endpoint(endpoint_name: str):
    """
    Helper function to test a single endpoint for detailed analysis with authentication
    """
    tester = CedroTechAPITester()
    return tester.test_specific_endpoint(endpoint_name)

def quick_auth_test():
    """
    Quick function to test just authentication
    """
    print("🔐 QUICK AUTHENTICATION TEST")
    print("=" * 40)
    
    tester = CedroTechAPITester()
    
    if tester.authenticate():
        print("✅ Authentication successful!")
        
        # Test one simple endpoint to verify it works
        print("\n📊 Testing one endpoint to verify authentication...")
        result = tester.test_endpoint(
            'quote_test',
            f"{tester.base_url}/services/quotes/quote/VALE3",
            'Quick quote test to verify authentication'
        )
        
        if result.get('success'):
            print("✅ Authenticated requests working!")
            print(f"   Status: {result['status_code']}")
            print(f"   Response time: {result['response_time_ms']}ms")
            if result.get('data_count'):
                print(f"   Data items: {result['data_count']}")
        else:
            print(f"⚠️ Authentication may not be working properly")
            print(f"   Status: {result.get('status_code', 'Unknown')}")
    else:
        print("❌ Authentication failed!")

if __name__ == "__main__":
    import sys
    
    # Allow running specific tests
    if len(sys.argv) > 1:
        if sys.argv[1] == "auth":
            quick_auth_test()
        elif sys.argv[1] == "endpoint":
            if len(sys.argv) > 2:
                test_single_endpoint(sys.argv[2])
            else:
                print("Usage: python test_all_cedrotech_endpoints.py endpoint <endpoint_name>")
        else:
            main()
    else:
        main()
