#!/usr/bin/env python3
"""
CedroTech Forex Contract Manager
Specifically designed to maintain monthly forex contracts to avoid CedroTech fees
Focus on Mini Dollar (WDO) futures for BTG Pactual integration
"""

import json
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import os
from cedrotech_real_api import CedroTechRealAPI

class ForexContractManager:
    """
    Manages monthly forex contracts to avoid CedroTech fees
    Focus on Mini Dollar (WDO) and Full Dollar (DOL) futures
    """
    
    def __init__(self):
        self.real_api = CedroTechRealAPI()
        
        # Preferred forex instruments (in order of preference)
        self.preferred_instruments = [
            'WDO25',   # Mini Dollar 2025 (lowest margin)
            'WDOj25',  # Mini Dollar January 2025
            'WDOx25',  # Mini Dollar specific month
            'DOL25',   # Full Dollar 2025 (higher margin)
            'DOLj25',  # Full Dollar January 2025
        ]
        
        # Contract tracking
        self.current_contract = None
        self.contract_expiry = None
        self.last_contract_check = None
        
        # Load state
        self.state_file = "forex_contract_state.json"
        self.load_state()
    
    def load_state(self):
        """Load contract state from file"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                
                self.current_contract = state.get('current_contract')
                self.contract_expiry = state.get('contract_expiry')
                self.last_contract_check = state.get('last_contract_check')
                
                print(f"📋 LOADED FOREX CONTRACT STATE:")
                print(f"   Current Contract: {self.current_contract}")
                print(f"   Expiry: {self.contract_expiry}")
                
        except Exception as e:
            print(f"⚠️ Could not load forex state: {e}")
            self.initialize_state()
    
    def save_state(self):
        """Save contract state to file"""
        try:
            state = {
                'current_contract': self.current_contract,
                'contract_expiry': self.contract_expiry,
                'last_contract_check': datetime.now().isoformat(),
                'last_update': datetime.now().isoformat()
            }
            
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
                
        except Exception as e:
            print(f"⚠️ Could not save forex state: {e}")
    
    def initialize_state(self):
        """Initialize default state"""
        self.current_contract = None
        self.contract_expiry = None
        self.last_contract_check = None
        print("🆕 INITIALIZED FOREX CONTRACT STATE")
    
    def get_available_contracts(self) -> List[Dict]:
        """Get list of available forex contracts with current prices"""
        print("🔍 CHECKING AVAILABLE FOREX CONTRACTS...")
        
        available_contracts = []
        
        for instrument in self.preferred_instruments:
            try:
                # Get quote for the instrument
                quote_url = f"{self.real_api.base_url}/services/quotes/quote/{instrument}"
                
                # Use the session from real_api if available
                response = requests.get(quote_url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data and not (isinstance(data, dict) and data.get('error')):
                        contract_info = {
                            'symbol': instrument,
                            'name': data.get('name', instrument),
                            'price': data.get('price', 'N/A'),
                            'volume': data.get('volume', 'N/A'),
                            'bid': data.get('bid', 'N/A'),
                            'ask': data.get('ask', 'N/A'),
                            'available': True
                        }
                        available_contracts.append(contract_info)
                        
                        print(f"   ✅ {instrument}: Available")
                        print(f"      Name: {contract_info['name']}")
                        print(f"      Price: {contract_info['price']}")
                
                time.sleep(0.5)  # Be respectful to API
                
            except Exception as e:
                print(f"   ❌ {instrument}: Error checking - {e}")
                continue
        
        return available_contracts
    
    def select_best_contract(self, available_contracts: List[Dict]) -> Optional[Dict]:
        """Select the best contract to maintain"""
        if not available_contracts:
            print("❌ No available contracts found")
            return None
        
        print("🎯 SELECTING BEST CONTRACT...")
        
        # Prefer Mini Dollar (WDO) over Full Dollar (DOL) for lower margin
        wdo_contracts = [c for c in available_contracts if 'WDO' in c['symbol']]
        dol_contracts = [c for c in available_contracts if 'DOL' in c['symbol'] and 'WDO' not in c['symbol']]
        
        if wdo_contracts:
            selected = wdo_contracts[0]  # Take first available WDO
            print(f"✅ SELECTED: {selected['symbol']} (Mini Dollar - Lower margin)")
            return selected
        elif dol_contracts:
            selected = dol_contracts[0]  # Take first available DOL
            print(f"✅ SELECTED: {selected['symbol']} (Full Dollar)")
            return selected
        else:
            selected = available_contracts[0]  # Take any available
            print(f"✅ SELECTED: {selected['symbol']} (Best available)")
            return selected
    
    def check_contract_needs_renewal(self) -> bool:
        """Check if we need to renew/establish a contract"""
        now = datetime.now()
        
        # If no current contract, we need one
        if not self.current_contract:
            print("🔄 NO CURRENT CONTRACT - Need to establish one")
            return True
        
        # If contract expiry is approaching (within 5 days), renew
        if self.contract_expiry:
            try:
                expiry_date = datetime.fromisoformat(self.contract_expiry)
                days_to_expiry = (expiry_date - now).days
                
                if days_to_expiry <= 5:
                    print(f"⚠️ CONTRACT EXPIRING IN {days_to_expiry} DAYS - Need to renew")
                    return True
                else:
                    print(f"✅ Current contract valid for {days_to_expiry} days")
                    return False
            except:
                print("⚠️ Invalid expiry date - Need to check contract")
                return True
        
        # If we haven't checked in over a week, check
        if self.last_contract_check:
            try:
                last_check = datetime.fromisoformat(self.last_contract_check)
                days_since_check = (now - last_check).days
                
                if days_since_check >= 7:
                    print(f"🔍 Haven't checked in {days_since_check} days - Verifying contract")
                    return True
            except:
                return True
        
        return False
    
    def establish_monthly_contract(self, use_real_trading: bool = False) -> bool:
        """Establish or renew monthly forex contract"""
        print("\n💰 ESTABLISHING MONTHLY FOREX CONTRACT")
        print("🎯 Goal: Maintain contract to avoid CedroTech fees")
        print("-" * 50)
        
        # Get available contracts
        available_contracts = self.get_available_contracts()
        
        if not available_contracts:
            print("❌ No forex contracts available")
            return False
        
        # Select best contract
        selected_contract = self.select_best_contract(available_contracts)
        
        if not selected_contract:
            print("❌ Could not select a contract")
            return False
        
        # Execute the order
        success = False
        
        if use_real_trading:
            success = self._place_real_forex_order(selected_contract)
        else:
            success = self._simulate_forex_order(selected_contract)
        
        if success:
            # Update state
            self.current_contract = selected_contract['symbol']
            # Set expiry to end of next month for safety
            next_month = datetime.now() + timedelta(days=35)
            self.contract_expiry = next_month.isoformat()
            self.save_state()
            
            print(f"✅ FOREX CONTRACT ESTABLISHED!")
            print(f"   Contract: {self.current_contract}")
            print(f"   Estimated Expiry: {next_month.strftime('%Y-%m-%d')}")
            print(f"   Purpose: Avoid CedroTech monthly fees")
            
            return True
        else:
            print("❌ Failed to establish forex contract")
            return False
    
    def _place_real_forex_order(self, contract: Dict) -> bool:
        """Place real forex order through CedroTech API"""
        print(f"🔥 PLACING REAL FOREX ORDER: {contract['symbol']}")
        
        try:
            # For futures, typically 1 contract is sufficient
            quantity = 1
            
            # Try to get a reasonable price (use ask price or market price)
            price = contract.get('ask') or contract.get('price')
            
            if not price or price == 'N/A':
                # Use a reasonable estimated price for futures
                if 'WDO' in contract['symbol']:
                    price = 5.50  # Typical Mini Dollar price range
                elif 'DOL' in contract['symbol']:
                    price = 5.50  # Typical Full Dollar price range
                else:
                    price = 10.0  # Conservative estimate
            
            print(f"   Symbol: {contract['symbol']}")
            print(f"   Quantity: {quantity} contract(s)")
            print(f"   Price: R${price:.2f}")
            
            # Place the order using the real API
            response = self.real_api.place_buy_order(
                symbol=contract['symbol'],
                quantity=quantity,
                price=float(price)
            )
            
            if response and response.get('success'):
                print(f"✅ REAL FOREX CONTRACT ESTABLISHED!")
                print(f"   Order ID: {response.get('order_id')}")
                return True
            else:
                print(f"❌ REAL FOREX ORDER FAILED: {response.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ FOREX ORDER ERROR: {e}")
            return False
    
    def _simulate_forex_order(self, contract: Dict) -> bool:
        """Simulate forex order for testing"""
        print(f"📊 SIMULATING FOREX ORDER: {contract['symbol']}")
        print(f"   This would establish 1 contract to avoid CedroTech fees")
        print(f"   Contract Type: {'Mini Dollar' if 'WDO' in contract['symbol'] else 'Full Dollar' if 'DOL' in contract['symbol'] else 'Other'}")
        print(f"   ✅ SIMULATION SUCCESSFUL")
        return True
    
    def get_contract_status(self) -> Dict:
        """Get current contract status"""
        return {
            'current_contract': self.current_contract,
            'contract_expiry': self.contract_expiry,
            'last_check': self.last_contract_check,
            'days_to_expiry': self._days_to_expiry(),
            'needs_renewal': self.check_contract_needs_renewal()
        }
    
    def _days_to_expiry(self) -> Optional[int]:
        """Calculate days to contract expiry"""
        if not self.contract_expiry:
            return None
        
        try:
            expiry_date = datetime.fromisoformat(self.contract_expiry)
            return (expiry_date - datetime.now()).days
        except:
            return None
    
    def generate_forex_report(self) -> str:
        """Generate forex contract status report"""
        status = self.get_contract_status()
        
        report = []
        report.append("💰 FOREX CONTRACT STATUS REPORT")
        report.append("=" * 50)
        report.append(f"🎯 Purpose: Avoid CedroTech monthly fees")
        report.append(f"🏦 Broker: BTG Pactual")
        report.append("")
        
        if status['current_contract']:
            report.append(f"📋 CURRENT CONTRACT:")
            report.append(f"   Symbol: {status['current_contract']}")
            
            if status['days_to_expiry'] is not None:
                report.append(f"   Days to Expiry: {status['days_to_expiry']}")
                
                if status['days_to_expiry'] <= 5:
                    report.append(f"   ⚠️ RENEWAL NEEDED SOON!")
                else:
                    report.append(f"   ✅ Contract Active")
            
            report.append(f"   Last Check: {status['last_check'] or 'Never'}")
        else:
            report.append(f"❌ NO ACTIVE CONTRACT")
            report.append(f"   Need to establish forex contract")
        
        report.append("")
        report.append(f"🔄 NEXT ACTION:")
        if status['needs_renewal']:
            report.append(f"   Establish/renew forex contract")
        else:
            report.append(f"   Continue monitoring")
        
        return "\n".join(report)

def main():
    """Test the forex contract manager"""
    print("🚀 CEDROTECH FOREX CONTRACT MANAGER")
    print("=" * 60)
    
    manager = ForexContractManager()
    
    # Check current status
    print(manager.generate_forex_report())
    
    # Check if we need a contract
    if manager.check_contract_needs_renewal():
        print("\n🔄 ESTABLISHING FOREX CONTRACT...")
        
        # Ask user for trading mode
        print("\n💰 TRADING MODE:")
        print("1. 📊 SIMULATION (Safe testing)")
        print("2. 🔥 REAL TRADING (Actual contract)")
        
        choice = input("Choose mode (1 or 2): ").strip()
        use_real = choice == "2"
        
        if use_real:
            print("⚠️ WARNING: This will place a real forex contract!")
            confirm = input("Type 'YES' to confirm: ").strip()
            if confirm != 'YES':
                print("❌ Operation cancelled")
                return
        
        success = manager.establish_monthly_contract(use_real_trading=use_real)
        
        if success:
            print("\n" + manager.generate_forex_report())
        else:
            print("\n❌ Failed to establish contract")
    else:
        print("\n✅ Current forex contract is sufficient")

if __name__ == "__main__":
    main()
