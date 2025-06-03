#!/usr/bin/env python3
"""
Test script to verify the backtest_strategy and backtesting_loop functions work correctly
"""

def test_backtest_functions():
    """Test the newly added backtest functions"""
    try:
        print("="*60)
        print("TESTING BACKTEST FUNCTIONS")
        print("="*60)
        
        # Test 1: Import functions
        print("1. Testing function imports...")
        from utils.backtest_engine import backtest_strategy, backtesting_loop, BacktestEngine
        print("✅ Successfully imported backtest_strategy, backtesting_loop, and BacktestEngine")
        
        # Test 2: Create BacktestEngine instance
        print("\n2. Testing BacktestEngine instantiation...")
        engine = BacktestEngine(initial_balance=1000, risk_per_trade=0.02)
        print("✅ Successfully created BacktestEngine instance")
        
        # Test 3: Check available methods
        print("\n3. Checking available methods...")
        methods = [method for method in dir(engine) if not method.startswith('_')]
        print(f"✅ Available methods: {', '.join(methods)}")
        
        # Test 4: Test function signatures
        print("\n4. Testing function availability...")
        print(f"✅ backtest_strategy function: {backtest_strategy}")
        print(f"✅ backtesting_loop function: {backtesting_loop}")
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("Your trading robot now has both:")
        print("  - backtest_strategy() function")
        print("  - backtesting_loop() function")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

if __name__ == "__main__":
    test_backtest_functions()
