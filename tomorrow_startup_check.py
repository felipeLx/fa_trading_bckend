#!/usr/bin/env python3
"""
Quick Robot Startup Verification for Tomorrow
Run this right before starting the robot to ensure everything is optimized
"""

import json
import os
from datetime import datetime

def verify_optimizations():
    """Verify that all optimizations are in place"""
    print("🚀 ROBOT STARTUP VERIFICATION")
    print("=" * 50)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 1. Check robot state reset
        print("\n1️⃣ Checking Robot State...")
        state_file = "integrated_cedrotech_robot_state.json"
        
        if os.path.exists(state_file):
            with open(state_file, 'r') as f:
                state = json.load(f)
            
            today = datetime.now().strftime('%Y-%m-%d')
            if state.get('last_trade_date') == today:
                print("   ✅ Robot state updated for today")
            else:
                print(f"   ⚠️ Robot state shows: {state.get('last_trade_date')}")
        else:
            print("   🆕 Fresh robot state will be created")
        
        # 2. Test robot initialization with new settings
        print("\n2️⃣ Testing Optimized Configuration...")
        
        from integrated_cedrotech_robot import IntegratedCedroTechRobot
        robot = IntegratedCedroTechRobot(paper_trading=True)
        
        print(f"   ✅ Confidence Threshold: {robot.confidence_threshold}% (was 70%)")
        print(f"   ✅ Strong Signal Threshold: {robot.strong_signal_threshold}% (was 85%)")
        print(f"   ✅ Max Daily Trades: {robot.max_daily_trades} (was 5)")
        print(f"   ✅ Asset Universe: {len(robot.asset_universe)} stocks")
        
        # 3. Verify optimizations applied
        print("\n3️⃣ Optimization Status...")
        
        optimizations_applied = 0
        total_optimizations = 3
        
        if robot.confidence_threshold <= 65.0:
            print("   ✅ Confidence threshold lowered for more opportunities")
            optimizations_applied += 1
        else:
            print("   ❌ Confidence threshold still too high")
            
        if robot.strong_signal_threshold <= 80.0:
            print("   ✅ Strong signal threshold lowered")
            optimizations_applied += 1
        else:
            print("   ❌ Strong signal threshold still too high")
            
        if robot.max_daily_trades >= 8:
            print("   ✅ Daily trade limit increased")
            optimizations_applied += 1
        else:
            print("   ❌ Daily trade limit not increased")
        
        # 4. Final readiness check
        print("\n" + "=" * 50)
        print("📊 READINESS ASSESSMENT")
        print(f"   Optimizations Applied: {optimizations_applied}/{total_optimizations}")
        
        if optimizations_applied == total_optimizations:
            print("   🚀 FULLY OPTIMIZED - Ready for launch!")
            print("   🎯 Expected: More trading opportunities today")
            print("   📈 Expected: More signals above threshold")
            print("   🔄 Expected: Successful analysis cycles")
        elif optimizations_applied >= 2:
            print("   ⚠️ MOSTLY OPTIMIZED - Should work better")
        else:
            print("   ❌ OPTIMIZATIONS FAILED - Manual check needed")
        
        # 5. Launch command
        print("\n🎯 LAUNCH COMMAND:")
        print("   python integrated_cedrotech_robot.py")
        print("   (Choose 'y' for continuous operation)")
        
        print("\n🔍 WHAT TO WATCH FOR:")
        print("   • ✅ CYCLE COMPLETED messages every 5 minutes")
        print("   • 📊 'Total Analyzed: 51' in each cycle")
        print("   • 🎯 'Above Threshold' count > 0")
        print("   • 💪 'Highest Confidence Today' values")
        print("   • 🔄 'ASSET SWITCH RECOMMENDED' messages")
        
        return optimizations_applied >= 2
        
    except Exception as e:
        print(f"\n❌ VERIFICATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = verify_optimizations()
    
    if success:
        print("\n🎉 VERIFICATION SUCCESSFUL!")
        print("🚀 Robot is optimized and ready for trading!")
    else:
        print("\n⚠️ VERIFICATION ISSUES FOUND")
        print("🔧 Manual configuration check recommended")
    
    print("\n🌅 Good luck with today's trading session!")
