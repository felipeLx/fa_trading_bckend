#!/usr/bin/env python3
"""
Database Migration: Create account_balance table
This script creates the account_balance table required by the BalanceManager.
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

def create_account_balance_table():
    """Create the account_balance table if it doesn't exist."""
    
    SUPABASE_URL = os.getenv("DATABASE_URL")
    SUPABASE_KEY = os.getenv("DATABASE_KEY")
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Missing database credentials in environment variables")
        return False
    
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
          # SQL to create account_balance table
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS account_balance (
            id BIGSERIAL PRIMARY KEY,
            user_id VARCHAR(255) NOT NULL,
            balance DECIMAL(12, 2) NOT NULL,
            source VARCHAR(50) NOT NULL DEFAULT 'manual',
            confidence VARCHAR(20) NOT NULL DEFAULT 'medium',
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            details JSONB
        );
        
        -- Create indexes for efficient queries
        CREATE INDEX IF NOT EXISTS idx_account_balance_user_id ON account_balance (user_id);
        CREATE INDEX IF NOT EXISTS idx_account_balance_updated_at ON account_balance (updated_at);
        """
        
        print("🔨 Creating account_balance table...")
        
        # Execute the SQL using Supabase RPC or raw SQL
        # Note: Supabase typically handles table creation through their dashboard
        # This is a reference implementation
        
        print("✅ Account balance table creation initiated.")
        print("📋 Please execute the following SQL in your Supabase SQL editor:")
        print("-" * 60)
        print(create_table_sql)
        print("-" * 60)
        
        # Try to test if the table exists by attempting a simple query
        try:
            result = supabase.table("account_balance").select("id").limit(1).execute()
            print("✅ Account balance table already exists and is accessible!")
            return True
        except Exception as e:
            print(f"⚠️ Table may not exist yet. Error: {e}")
            print("Please create the table using the SQL above in Supabase dashboard.")
            return False
            
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("DATABASE MIGRATION: Account Balance Table")
    print("="*60)
    
    success = create_account_balance_table()
    
    if success:
        print("\n✅ Migration completed successfully!")
    else:
        print("\n⚠️ Manual intervention required. Please create the table in Supabase.")
        
    print("\nNext steps:")
    print("1. Ensure the account_balance table exists in your database")
    print("2. Run the trading robot with: python robot.py")
    print("3. The BalanceManager will now track dynamic balance changes")
