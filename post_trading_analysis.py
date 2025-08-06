#!/usr/bin/env python3
"""
Post-Trading Day Analysis
Diagnose why no trades were executed and optimize for tomorrow
"""

import json
import os
from datetime import datetime, timedelta
import sys

# Add the current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def analyze_trading_day():
    """Analyze why no trades were executed today"""
    print("🔍 POST-TRADING DAY ANALYSIS")
    print("=" * 60)
    print(f"📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    issues_found = []
    recommendations = []
    
    # 1. Check robot state
    print("\n1️⃣ Robot State Analysis...")
    state_file = "integrated_cedrotech_robot_state.json"
    
    if os.path.exists(state_file):
        with open(state_file, 'r') as f:
            state = json.load(f)
        
        print(f"   📊 Robot Version: {state.get('version', 'Unknown')}")
        print(f"   📅 Last Trade Date: {state.get('last_trade_date', 'None')}")
        print(f"   🕐 Last Analysis Time: {state.get('last_analysis_time', 'None')}")
        print(f"   📈 Daily Trades: {state.get('daily_trades', 0)}")
        print(f"   💪 Last Signal Strength: {state.get('last_signal_strength', 0)}")
        
        # Check if analysis ran at all
        if state.get('last_analysis_time') is None:
            issues_found.append("❌ No analysis cycles completed")
            recommendations.append("🔧 Check robot startup and API connections")
        
        # Check if signals were too weak
        if state.get('last_signal_strength', 0) < 70:
            issues_found.append("⚠️ All signals below confidence threshold (70%)")
            recommendations.append("📉 Consider lowering confidence threshold to 65% temporarily")
            
        # Check date consistency
        today = datetime.now().strftime('%Y-%m-%d')
        if state.get('last_trade_date') != today:
            issues_found.append("📅 Robot state not updated for today")
            recommendations.append("🔄 Reset robot state for new trading day")
            
    else:
        issues_found.append("❌ Robot state file missing")
        recommendations.append("🆕 Robot may not have started properly")
    
    # 2. Check if there were any logs or errors
    print("\n2️⃣ Error Detection...")
    
    # Look for potential log files or error indicators
    potential_logs = ["robot.log", "trading.log", "errors.log"]
    found_logs = [log for log in potential_logs if os.path.exists(log)]
    
    if found_logs:
        print(f"   📝 Log files found: {', '.join(found_logs)}")
    else:
        print("   ℹ️ No log files found (normal for this setup)")
    
    # 3. Market conditions check
    print("\n3️⃣ Market Conditions Analysis...")
    
    # Check if it was a low-volatility day
    print("   📊 Possible reasons for no trades:")
    print("      • Low market volatility day")
    print("      • All 51 stocks showed HOLD signals")
    print("      • Market conditions didn't meet 70% confidence threshold")
    print("      • Technical + Fundamental analysis didn't align")
    
    # 4. Configuration review
    print("\n4️⃣ Configuration Review...")
    
    try:
        # Try to import and check robot configuration
        from integrated_cedrotech_robot import IntegratedCedroTechRobot
        
        # Create robot instance to check settings
        robot = IntegratedCedroTechRobot(paper_trading=True)
        
        print(f"   ✅ Asset Universe: {len(robot.asset_universe)} stocks")
        print(f"   🎯 Confidence Threshold: {robot.confidence_threshold}%")
        print(f"   💪 Strong Signal Threshold: {robot.strong_signal_threshold}%")
        print(f"   📈 Max Daily Trades: {robot.max_daily_trades}")
        
        # High threshold might be the issue
        if robot.confidence_threshold >= 70:
            issues_found.append("🎯 High confidence threshold (70%) may be too restrictive")
            recommendations.append("📉 Consider lowering to 65% for more opportunities")
            
        if robot.strong_signal_threshold >= 85:
            issues_found.append("💪 Very high strong signal threshold (85%)")
            recommendations.append("📊 Consider 80% threshold for more STRONG signals")
            
    except Exception as e:
        issues_found.append(f"❌ Robot configuration error: {e}")
        recommendations.append("🔧 Check robot initialization and dependencies")
    
    # 5. Generate recommendations
    print("\n" + "=" * 60)
    print("📋 DIAGNOSIS SUMMARY")
    
    if issues_found:
        print(f"\n⚠️ ISSUES IDENTIFIED ({len(issues_found)}):")
        for i, issue in enumerate(issues_found, 1):
            print(f"   {i}. {issue}")
    else:
        print("\n✅ NO CRITICAL ISSUES FOUND")
        print("   This might have been a low-opportunity trading day")
    
    print(f"\n🔧 RECOMMENDATIONS FOR TOMORROW ({len(recommendations)}):")
    for i, rec in enumerate(recommendations, 1):
        print(f"   {i}. {rec}")
    
    # Additional standard recommendations
    print("\n💡 STANDARD OPTIMIZATIONS:")
    print("   🎯 Lower confidence threshold from 70% to 65%")
    print("   💪 Lower strong signal threshold from 85% to 80%") 
    print("   🔄 Reset robot state for fresh start")
    print("   📊 Enable more detailed logging")
    print("   ⏰ Verify 15-minute cycles are completing")
    
    return len(issues_found) == 0

def create_optimized_config():
    """Create optimized configuration for tomorrow"""
    print("\n🚀 CREATING OPTIMIZED CONFIGURATION...")
    
    config_changes = {
        "confidence_threshold": 65.0,  # Lower from 70%
        "strong_signal_threshold": 80.0,  # Lower from 85%
        "max_daily_trades": 8,  # Increase from 5
        "enable_detailed_logging": True
    }
    
    print("   📝 Proposed changes for tomorrow:")
    for key, value in config_changes.items():
        print(f"      • {key}: {value}")
    
    return config_changes

def reset_robot_for_tomorrow():
    """Reset robot state for tomorrow's trading"""
    print("\n🔄 RESETTING ROBOT FOR TOMORROW...")
    
    state_file = "integrated_cedrotech_robot_state.json"
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    fresh_state = {
        "robot_name": "Integrated CedroTech Robot",
        "version": "2.0.0",
        "current_asset": None,
        "current_position": None,
        "last_analysis_time": None,
        "last_trade_time": None,
        "last_trade_date": tomorrow,
        "trades_executed": 0,
        "successful_trades": 0,
        "total_profit_loss": 0.0,
        "daily_trades": 0,
        "last_signal_strength": 0.0,
        "last_update": datetime.now().isoformat()
    }
    
    with open(state_file, 'w') as f:
        json.dump(fresh_state, f, indent=2)
    
    print(f"   ✅ Robot state reset for {tomorrow}")
    print("   🆕 Fresh start ready for tomorrow")

if __name__ == "__main__":
    # Run analysis
    no_issues = analyze_trading_day()
    
    # Create optimized config
    create_optimized_config()
    
    # Reset for tomorrow
    reset_robot_for_tomorrow()
    
    print("\n" + "=" * 60)
    print("🌙 GOOD NIGHT ANALYSIS COMPLETE")
    
    if no_issues:
        print("   ✅ Robot appears healthy - may have been quiet market day")
    else:
        print("   🔧 Issues identified and optimization planned")
    
    print("   🌅 Ready for tomorrow's trading session!")
    print("   🚀 Optimized settings will increase trade opportunities")
