#!/usr/bin/env python3
"""
Script to manually reset the robot state file.
Use this before starting the robot for a new trading day.
"""

import json
import os
from datetime import datetime

STATE_FILE = 'robot_state.json'

def reset_robot_state():
    """Reset the robot state to start fresh analysis"""
    print("🔄 Resetting robot state for fresh analysis...")
    
    new_state = {
        'holding_asset': None,
        'position_size': 0,
        'buy_price': None,
        'stop_loss': None,
        'take_profit': None,
        'last_analysis_date': None
    }
    
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(new_state, f, indent=2)
        
        print("✅ Robot state reset successfully!")
        print("The robot will now perform fresh asset analysis when started.")
        
        if os.path.exists(STATE_FILE):
            print(f"📁 State file location: {os.path.abspath(STATE_FILE)}")
        
    except Exception as e:
        print(f"❌ Error resetting state: {e}")

if __name__ == "__main__":
    print("="*50)
    print("TRADING ROBOT - STATE RESET")
    print("="*50)
    
    # Show current state if it exists
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                current_state = json.load(f)
            print("Current state:")
            for key, value in current_state.items():
                print(f"  {key}: {value}")
            print()
        except:
            print("Current state file is corrupted or unreadable.")
    else:
        print("No current state file found.")
    
    confirm = input("Reset robot state? (y/n): ").strip().lower()
    
    if confirm == 'y':
        reset_robot_state()
    else:
        print("State reset cancelled.")
