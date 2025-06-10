#!/usr/bin/env python3
"""
Debug script to test CedroTech authentication with different approaches
This will help us understand the exact API requirements.
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

def test_simple_auth():
    """Test the exact format from the working example"""
    print("="*60)
    print("DEBUGGING CEDROTECH AUTHENTICATION")
    print("="*60)
    print()
    
    username = os.getenv('CEDROTECH_USERNAME', '')
    password = os.getenv('CEDROTECH_PASSWORD', '') 
    base_url = "https://webfeeder.cedrotech.com"
    
    print(f"🔧 Testing with:")
    print(f"   Username: {username}")
    print(f"   Password: {'*' * len(password) if password else 'NOT SET'}")
    print(f"   Base URL: {base_url}")
    print()
    
    # Test 1: Exact format from your working example
    print("🧪 TEST 1: Exact format from working example")
    print("-" * 40)
    
    try:
        url = f"{base_url}/SignIn?login={username}&password={password}"
        headers = {"accept": "application/json"}
        
        print(f"   URL: {url}")
        print(f"   Headers: {headers}")
        
        response = requests.post(url, headers=headers)
        
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   JSON Data: {data}")
                print(f"   Data Type: {type(data)}")
            except:
                print(f"   Not JSON, raw text: '{response.text}'")
        
    except Exception as e:
        print(f"   ERROR: {e}")
    
    print()
    
    # Test 2: With URL encoding
    print("🧪 TEST 2: With URL encoding")
    print("-" * 40)
    
    try:
        # URL encode special characters
        encoded_password = password.replace('@', '%40').replace('*', '%2A').replace('#', '%23')
        url = f"{base_url}/SignIn?login={username}&password={encoded_password}"
        headers = {"accept": "application/json"}
        
        print(f"   URL: {url}")
        
        response = requests.post(url, headers=headers)
        
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
    except Exception as e:
        print(f"   ERROR: {e}")
    
    print()
    
    # Test 3: Test environment variables
    print("🧪 TEST 3: Test environment variables")
    print("-" * 40)
    
    env_username = os.getenv('CEDROTECH_USERNAME')
    env_password = os.getenv('CEDROTECH_PASSWORD')
    
    print(f"   ENV Username: {env_username}")
    print(f"   ENV Password: {'*' * len(env_password) if env_password else 'NOT SET'}")
    
    if env_username and env_password:
        try:
            url = f"{base_url}/SignIn?login={env_username}&password={env_password}"
            headers = {"accept": "application/json"}
            
            response = requests.post(url, headers=headers)
            
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            
        except Exception as e:
            print(f"   ERROR: {e}")
    else:
        print("   ⚠️  Environment variables not set")
    
    print()
    
    # Test 4: Test different credential formats
    print("🧪 TEST 4: Test different credential formats")
    print("-" * 40)
    
    test_credentials = [
        (password),  
        (password),  
        (f"btg{username}", password),  # Combined format
    ]
    
    for test_user, test_pass in test_credentials:
        try:
            print(f"   Testing: {test_user} / {'*' * len(test_pass)}")
            url = f"{base_url}/SignIn?login={test_user}&password={test_pass}"
            response = requests.post(url, headers={"accept": "application/json"})
            print(f"     Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            print(f"     ERROR: {e}")
    
    print()
    print("="*60)
    print("NEXT STEPS:")
    print("1. Check which combination returns 'true' or successful response")
    print("2. Update .env file with correct credentials")
    print("3. Update CedroTech API code with working format")
    print("="*60)

if __name__ == "__main__":
    test_simple_auth()
