# 🚀 MONDAY MARKET HOURS ACTION PLAN

## ⏰ TIMING (Monday, June 9, 2025)

**Brazilian Market Hours:**
- **Pre-market:** Before 09:00 BRT
- **Market Open:** 09:00 BRT 
- **Active Trading:** 10:00-16:00 BRT (best liquidity)
- **Force Close:** 16:30 BRT (options robot)
- **Market Close:** 17:30 BRT

## 📋 STEP-BY-STEP TESTING PLAN

### **Step 1: Pre-Market Check (Before 09:00)**
```bash
python check_market_status.py
```
Should show: "Pre-market - Market opens in X hours"

### **Step 2: Market Open Validation (09:00+)**
```bash
python check_market_status.py
```
Should show: "✅ MARKET IS OPEN"

### **Step 3: Test Live Options Quotes (09:15+)**
```bash
python test_options_live_quotes.py
```
**Expected Results:**
- ✅ Real bid/ask quotes (not 0.00/0.00)
- ✅ valeg565w2 shows active quotes
- ✅ valeg545w2 shows active quotes
- ✅ Volume > 0, Open Interest > 1000

### **Step 4: Options Robot Paper Trading (09:30+)**
```bash
python daily_options_startup.py
python options_robot.py
```
Choose: **1 (Paper Trading)**

## 🎯 SUCCESS CRITERIA

### **✅ WHAT YOU WANT TO SEE:**
1. **Live Quotes:**
   - Bid > 0.00, Ask > 0.00
   - Spread < 15%
   - Volume > 10 contracts

2. **Robot Validation:**
   - "OPTION IS TRADEABLE" message
   - Position sizing calculates correctly
   - Risk management working (1% max)

### **⚠️ POTENTIAL ISSUES:**

#### **If still getting 0.00/0.00 quotes:**
1. Check if VALE3 stock is trading
2. Verify options haven't expired
3. Try different VALE strike prices

#### **If spreads are too wide (>20%):**
1. Normal for Brazilian options market
2. Wait for higher volume (10:00-15:00)
3. Consider this in your strategy

## 🔧 TROUBLESHOOTING COMMANDS

### **Check VALE3 Stock Status:**
```bash
python -c "
from utils.cedrotech_api_correct import CedroTechAPICorrect
api = CedroTechAPICorrect(paper_trading=True)
quote = api.get_quote('VALE3')
print(f'VALE3: {quote}')
"
```

### **Manual Options Quote Test:**
```bash
python -c "
from cedrotech_options_api import CedroTechOptionsAPI
api = CedroTechOptionsAPI()
quote = api.get_option_quote('valeg565w2')
print(f'valeg565w2: {quote}')
"
```

## 📊 MONITORING SCHEDULE

### **09:00-10:00:** Market Open Phase
- High volatility expected
- Wide spreads normal
- Focus on quote validation

### **10:00-15:00:** Active Trading Phase
- Best liquidity window
- Tightest spreads
- Ideal for robot testing

### **15:00-16:30:** Pre-Close Phase
- Volume may decrease
- Options robot will prepare to close
- Monitor force-close logic

### **16:30+:** Force Close Phase
- Options robot stops new trades
- Closes any open positions
- Safer than stock trading close

## 🎉 EXPECTED OUTCOMES

### **Phase 1 (Validation):** 
- [ ] Market status works
- [ ] Live quotes available
- [ ] At least 1 option tradeable

### **Phase 2 (Robot Testing):**
- [ ] Options robot starts successfully
- [ ] Paper trading mode works
- [ ] Position sizing correct
- [ ] Risk limits respected

### **Phase 3 (Understanding):**
- [ ] Options spreads behavior
- [ ] Time decay impact
- [ ] Volume patterns
- [ ] Brazilian market dynamics

## 🚨 IMPORTANT REMINDERS

1. **ONLY Paper Trading** until proven successful
2. **Brazilian time zone** awareness critical
3. **VALE3 stock price** affects option values
4. **Monday might be volatile** (weekend gap)
5. **Options expire** - check expiry dates

## 📞 NEXT STEPS AFTER MONDAY

### **If Successful:**
- Continue paper trading for 30 days
- Add more VALE options to scan
- Implement Greeks calculation
- Monitor performance metrics

### **If Issues Found:**
- Expand options target list
- Adjust spread tolerance
- Consider different strikes
- Check API rate limits

---

## 🎯 YOUR SYSTEMS ARE READY!

You have a complete dual robot architecture:
- ✅ **Stock Robot** (proven, profitable)
- ✅ **Options Robot** (specialized, conservative)
- ✅ **Testing Framework** (comprehensive validation)

**Monday Goal:** Validate that options quotes are live and robot can identify tradeable opportunities during Brazilian market hours!
