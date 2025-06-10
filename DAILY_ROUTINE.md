# 📋 Daily Trading Robot Routine

## 🌅 Every Morning (Before Trading)

### 1. **Daily Startup Check** ⭐ IMPORTANT
```powershell
python daily_startup.py
```
This script will:
- ✅ Verify your current balance (should show R$500.00 + any P&L from previous days)
- ✅ Check robot state file is updated with today's date
- ✅ Verify all environment variables are set
- ✅ Check if market is open
- ✅ Test position sizing calculations

### 2. **Start Trading Robot**
```powershell
python robot.py
```

## 🌆 During Trading (Optional Monitoring)

### **Check Balance Updates** (if needed)
```powershell
python test_balance_integration.py
```

### **View Current Balance Summary**
```python
from utils.balance_manager import BalanceManager
bm = BalanceManager()
print(bm.get_balance_summary())
```

## 🌙 End of Day (Optional)

### **Daily P&L Review**
The robot automatically tracks your balance changes. No manual action needed!

---

## ⚠️ **CRITICAL: What Changed from Before**

### ❌ **OLD (Dangerous) System:**
- Account balance was hardcoded at R$500
- Never updated after trades
- Could lead to overtrading and financial exposure

### ✅ **NEW (Secure) System:**
- Balance updates dynamically after every trade
- Real-time position sizing based on current balance
- Prevents overtrading with insufficient funds
- Automatic P&L calculation

---

## 🚨 **Daily Routine Summary**

**ONLY 2 STEPS NEEDED DAILY:**

1. **Morning:** `python daily_startup.py` (30 seconds)
2. **Start Trading:** `python robot.py`

**Everything else is automatic!** 🎉

---

## 🔧 **Troubleshooting**

### If balance shows incorrect amount:
```powershell
python setup_balance_system.py
```

### If you see database errors (42P01):
The system falls back gracefully to trade history calculation. Your trading is not affected.

### If position sizing seems wrong:
Check that your trades are being recorded in the database properly.

---

## 📊 **What the System Does Automatically**

- ✅ Updates balance after every buy/sell
- ✅ Calculates position sizes based on current balance
- ✅ Prevents trades you can't afford
- ✅ Tracks P&L from trade history
- ✅ Saves balance records to database
- ✅ Provides fallback if database is unavailable

**No more manual balance management!** The critical security vulnerability is now fixed.
