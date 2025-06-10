#!/usr/bin/env python3
"""
Setup Balance System for Trading Robot
Creates the account_balance table and initializes the starting balance.
"""

import os
from datetime import datetime, timezone
from dotenv import load_dotenv
from utils.database import supabase

load_dotenv()

def create_balance_table():
    """Create the account_balance table in Supabase."""
    print("🏗️ Creating account_balance table...")
    
    # SQL to create the account_balance table
    sql_commands = [
        """
        CREATE TABLE IF NOT EXISTS account_balance (
            id BIGSERIAL PRIMARY KEY,
            user_id TEXT NOT NULL,
            balance DECIMAL(15,2) NOT NULL,
            source TEXT NOT NULL,
            updated_at TIMESTAMPTZ DEFAULT NOW(),
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_account_balance_user_id 
        ON account_balance(user_id);
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_account_balance_updated_at 
        ON account_balance(updated_at DESC);
        """
    ]
    
    try:
        # Execute each SQL command
        for i, sql in enumerate(sql_commands, 1):
            print(f"   Executing SQL command {i}/3...")
            result = supabase.rpc('exec_sql', {'sql': sql.strip()}).execute()
            if result:
                print(f"   ✅ Command {i} executed successfully")
            else:
                print(f"   ❌ Command {i} failed")
                return False
        
        print("✅ Account balance table created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating table: {e}")
        print("\n📝 Manual Setup Required:")
        print("Please run these SQL commands in your Supabase SQL Editor:")
        print("-" * 60)
        for sql in sql_commands:
            print(sql)
        print("-" * 60)
        return False

def setup_initial_balance():
    """Setup the initial balance record."""
    user_id = os.getenv("USER_ID")
    initial_balance = 500.0
    
    print(f"💰 Setting up initial balance of R${initial_balance:,.2f} for user {user_id}")
    
    try:
        # Check if balance record already exists
        result = supabase.table("account_balance").select("*").eq("user_id", user_id).execute()
        
        if result.data:
            print(f"   ℹ️  Balance record already exists: R${result.data[-1]['balance']:,.2f}")
            return True
        
        # Insert initial balance record
        insert_result = supabase.table("account_balance").insert({
            "user_id": user_id,
            "balance": initial_balance,
            "source": "initial_setup",
            "updated_at": datetime.now(timezone.utc).isoformat()
        }).execute()
        
        if insert_result.data:
            print(f"✅ Initial balance record created: R${initial_balance:,.2f}")
            return True
        else:
            print("❌ Failed to create initial balance record")
            return False
            
    except Exception as e:
        print(f"❌ Error setting up initial balance: {e}")
        return False

def test_balance_system():
    """Test the balance system to ensure it's working."""
    print("\n🧪 Testing Balance System...")
    
    try:
        from utils.balance_manager import BalanceManager
        
        # Initialize balance manager
        balance_manager = BalanceManager()
        
        # Get current balance
        balance_info = balance_manager.get_current_balance()
        
        print(f"✅ Balance Manager working!")
        print(f"   Current Balance: R${balance_info['balance']:,.2f}")
        print(f"   Source: {balance_info['source']}")
        print(f"   Confidence: {balance_info['confidence']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Balance system test failed: {e}")
        return False

def main():
    """Main setup function."""
    print("🚀 Setting up Balance System for Trading Robot")
    print("=" * 50)
    
    # Step 1: Create table
    table_created = create_balance_table()
    
    # Step 2: Setup initial balance
    if table_created:
        balance_setup = setup_initial_balance()
    else:
        print("\n⚠️  Skipping balance setup due to table creation issues")
        balance_setup = False
    
    # Step 3: Test system
    if balance_setup:
        test_success = test_balance_system()
    else:
        test_success = False
    
    print("\n" + "=" * 50)
    if table_created and balance_setup and test_success:
        print("🎉 Balance System Setup Complete!")
        print("   Your trading robot is ready for live trading tomorrow.")
        print("   The hardcoded balance issue has been resolved.")
    else:
        print("⚠️  Setup incomplete. Please check errors above.")
        if not table_created:
            print("   - Database table needs to be created manually")
        if not balance_setup:
            print("   - Initial balance needs to be set manually")
        if not test_success:
            print("   - Balance system testing failed")

if __name__ == "__main__":
    main()
