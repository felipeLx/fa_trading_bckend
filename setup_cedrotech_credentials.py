#!/usr/bin/env python3
"""
CedroTech API Credentials Setup
Set up environment variables for REAL MONEY trading
"""

import os
from dotenv import load_dotenv, set_key

def setup_cedrotech_credentials():
    """Setup CedroTech API credentials for real trading"""
    print("🔐 CEDROTECH API CREDENTIALS SETUP")
    print("=" * 50)
    print("⚠️ WARNING: These credentials will be used for REAL MONEY trading!")
    print()
    
    # Load existing .env file
    env_file = '.env'
    load_dotenv(env_file)
    
    # Get existing values
    current_username = os.environ.get('CEDROTECH_USERNAME', '')
    current_user_id = os.environ.get('CEDROTECH_USER_ID', '')
    current_account = os.environ.get('CEDROTECH_ACCOUNT', '')
    
    print("Current Configuration:")
    print(f"   Username: {'SET' if current_username else 'NOT SET'}")
    print(f"   User ID: {'SET' if current_user_id else 'NOT SET'}")
    print(f"   Account: {'SET' if current_account else 'NOT SET'}")
    print()
    
    # Ask user if they want to update
    if all([current_username, current_user_id, current_account]):
        response = input("Credentials already configured. Update them? (y/n): ").lower()
        if response != 'y':
            print("✅ Using existing credentials")
            return True
    
    print("🔧 Enter your CedroTech API credentials:")
    print("   (These are the same credentials you use to login to CedroTech)")
    print()
    
    # Get credentials from user
    username = input("Username (login): ").strip()
    if not username:
        print("❌ Username is required!")
        return False
    
    user_id = input("User Identifier (user-identifier header): ").strip()
    if not user_id:
        print("❌ User Identifier is required!")
        return False
    
    account = input("Account Number: ").strip()
    if not account:
        print("❌ Account Number is required!")
        return False
    
    # Confirm before saving
    print("\n📋 Confirm Credentials:")
    print(f"   Username: {username}")
    print(f"   User ID: {user_id}")
    print(f"   Account: {account}")
    print()
    
    confirm = input("Save these credentials? (y/n): ").lower()
    if confirm != 'y':
        print("❌ Credentials not saved")
        return False
    
    # Save to .env file
    try:
        set_key(env_file, 'CEDROTECH_USERNAME', username)
        set_key(env_file, 'CEDROTECH_USER_ID', user_id)
        set_key(env_file, 'CEDROTECH_ACCOUNT', account)
        
        print("✅ Credentials saved to .env file")
        print()
        print("🔐 Security Notes:")
        print("   • .env file contains sensitive information")
        print("   • Never share or commit this file")
        print("   • Keep credentials secure")
        print()
        print("🚀 Ready for real money trading!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving credentials: {e}")
        return False

def test_credentials():
    """Test if credentials are properly configured"""
    print("\n🧪 Testing Credentials Configuration...")
    
    load_dotenv()
    
    username = os.environ.get('CEDROTECH_USERNAME')
    user_id = os.environ.get('CEDROTECH_USER_ID')
    account = os.environ.get('CEDROTECH_ACCOUNT')
    
    if all([username, user_id, account]):
        print("✅ All credentials configured")
        print(f"   Username: {username[:3]}...")
        print(f"   User ID: {user_id[:8]}...")
        print(f"   Account: {account[:4]}...")
        return True
    else:
        print("❌ Missing credentials:")
        if not username: print("   - CEDROTECH_USERNAME")
        if not user_id: print("   - CEDROTECH_USER_ID")
        if not account: print("   - CEDROTECH_ACCOUNT")
        return False

if __name__ == "__main__":
    success = setup_cedrotech_credentials()
    
    if success:
        test_credentials()
        print("\n🎯 Next Steps:")
        print("   1. Test with paper trading first")
        print("   2. Run: python petr4_geopolitical_robot.py")
        print("   3. Confirm all signals before real money")
    else:
        print("\n⚠️ Setup incomplete - fix issues before trading")
