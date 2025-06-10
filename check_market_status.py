#!/usr/bin/env python3
"""
Quick Market Status Checker
Check if the Brazilian B3 market is currently open for options trading
"""

from datetime import datetime
import pytz

def get_brazilian_time():
    """Get current Brazilian time (São Paulo timezone)"""
    br_tz = pytz.timezone('America/Sao_Paulo')
    return datetime.now(br_tz)

def is_b3_market_open():
    """Check if B3 market is currently open"""
    br_time = get_brazilian_time()
    
    # Check if it's a weekday (Monday=0, Sunday=6)
    weekday = br_time.weekday()
    if weekday >= 5:  # Saturday or Sunday
        return False, "Weekend"
    
    # Check market hours (9:00 - 17:30 BRT)
    current_hour = br_time.hour
    current_minute = br_time.minute
    current_time_minutes = current_hour * 60 + current_minute
    
    market_open_minutes = 9 * 60  # 9:00
    market_close_minutes = 17 * 60 + 30  # 17:30
    
    if current_time_minutes < market_open_minutes:
        return False, "Pre-market"
    elif current_time_minutes > market_close_minutes:
        return False, "After-market"
    else:
        return True, "Market hours"

def main():
    """Main market status check"""
    print("🇧🇷 B3 MARKET STATUS CHECKER")
    print("=" * 40)
    
    br_time = get_brazilian_time()
    is_open, status = is_b3_market_open()
    
    print(f"🕒 Brazilian time: {br_time.strftime('%H:%M:%S %Z')}")
    print(f"📅 Date: {br_time.strftime('%Y-%m-%d (%A)')}")
    print(f"📊 Market status: {status}")
    
    if is_open:
        print("✅ MARKET IS OPEN - Perfect for options testing!")
        print("\n🚀 READY TO RUN:")
        print("python test_options_live_quotes.py")
        print("python options_robot.py")
    else:
        print(f"❌ MARKET IS CLOSED ({status})")
        print("\n⏰ Market hours: Monday-Friday 09:00-17:30 BRT")
        
        if status == "Pre-market":
            # Calculate time until market opens
            market_open_time = br_time.replace(hour=9, minute=0, second=0, microsecond=0)
            time_until_open = market_open_time - br_time
            hours, remainder = divmod(time_until_open.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            print(f"📅 Market opens in: {hours}h {minutes}m")
        elif status == "After-market":
            # Calculate time until next market day
            print("📅 Market opens tomorrow at 09:00 BRT")
        elif status == "Weekend":
            # Calculate time until Monday
            days_until_monday = 7 - br_time.weekday()
            if days_until_monday == 7:  # If it's Sunday
                days_until_monday = 1
            print(f"📅 Market opens in {days_until_monday} day(s) (Monday 09:00 BRT)")

if __name__ == "__main__":
    main()
