#!/usr/bin/env python3
"""
Setup Initial Balance
This script sets up the initial balance record for the trading robot.
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime

# Load environment variables
load_dotenv()

def setup_initial_balance(initial_amount=500.0):
    """Set up the initial balance record in the database."""
    
    SUPABASE_URL = os.getenv("DATABASE_URL")
    SUPABASE_KEY = os.getenv("DATABASE_KEY")
    USER_ID = os.getenv("USER_ID")
    
    if not all([SUPABASE_URL, SUPABASE_KEY, USER_ID]):
        print("❌ Missing required environment variables")
        print("   Required: DATABASE_URL, DATABASE_KEY, USER_ID")
        return False
    
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        print(f"💰 Setting up initial balance: R${initial_amount:.2f}")
        print(f"👤 User ID: {USER_ID}")
        
        # First check if user already has a balance record
        existing_balance = supabase.table("account_balance").select("*").eq("user_id", USER_ID).execute()
        
        if existing_balance.data:
            print(f"📊 Found {len(existing_balance.data)} existing balance record(s)")
            latest_record = existing_balance.data[-1]
            print(f"   Latest balance: R${latest_record['balance']}")
            print(f"   Source: {latest_record['source']}")
            print(f"   Updated: {latest_record['updated_at']}")
            
            response = input("Do you want to add a new initial balance record? (y/n): ").strip().lower()
            if response != 'y':
                print("⏭️ Skipping balance setup")
                return True
        
        # Insert initial balance record
        balance_record = {
            "user_id": USER_ID,
            "balance": initial_amount,
            "source": "initial_setup",
            "confidence": "high",
            "updated_at": datetime.now().isoformat(),
            "details": {
                "setup_date": datetime.now().isoformat(),
                "setup_type": "manual_initial_balance",
                "note": "Initial trading balance setup"
            }
        }
        
        result = supabase.table("account_balance").insert(balance_record).execute()
        
        if result.data:
            print("✅ Initial balance record created successfully!")
            print(f"   Balance ID: {result.data[0]['id']}")
            print(f"   Amount: R${result.data[0]['balance']}")
            print(f"   Created: {result.data[0]['created_at']}")
            return True
        else:
            print("❌ Failed to create balance record")
            return False
            
    except Exception as e:
        if "does not exist" in str(e):
            print("❌ The account_balance table doesn't exist yet!")
            print("   Please run: python create_balance_table.py")
            print("   And execute the SQL in your Supabase dashboard first.")
        else:
            print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("SETUP INITIAL TRADING BALANCE")
    print("="*60)
    
    print("This script will set up your initial trading balance.")
    print("Current default: R$500.00")
    print()
    
    # Ask user to confirm amount
    try:
        amount_input = input("Enter your initial balance amount (or press Enter for R$500): ").strip()
        if amount_input:
            initial_amount = float(amount_input)
        else:
            initial_amount = 500.0
    except ValueError:
        print("❌ Invalid amount entered. Using default R$500.00")
        initial_amount = 500.0
    
    success = setup_initial_balance(initial_amount)
    
    if success:
        print(f"\n✅ Setup completed! Your trading balance is set to R${initial_amount:.2f}")
        print("\nNext steps:")
        print("1. Run: python test_balance_integration.py (to verify)")
        print("2. Run: python robot.py (to start trading)")
    else:
        print("\n❌ Setup failed. Please check the errors above.")
