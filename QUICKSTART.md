# AlgoGuard AI - Quick Start Guide

## ⚡ 30-Second Setup

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Start the App
```bash
python app.py
```

### Step 3: Open in Browser
```
http://localhost:5000
```

---

## 📝 First Time Setup

1. **Register Account**
   - Click "Register"
   - Enter: Username, Email, Password
   - Click "Register"

2. **Login**
   - Enter credentials
   - Click "Login"

3. **Add Algorand Address**
   - Go to "Settings"
   - Paste your 58-character Algorand address
   - Click "Save Algorand Address"
   - **Monitoring starts immediately!**

4. **View Dashboard**
   - Return to "Dashboard"
   - See real-time data, alerts, and charts

---

## 🎯 What to Expect

### Dashboard Shows:
- ✅ Current ALGO balance
- ✅ Price in USD
- ✅ Market cap
- ✅ Blockchain round number
- ✅ Risk score (AI-calculated)
- ✅ Alert history
- ✅ Balance trend chart
- ✅ Price history chart

### Data Updates:
- Dashboard: Every 3 seconds
- Price: Every 30 seconds
- Charts: Every 30 seconds

### Alerts Trigger When:
- Balance drops below 50 ALGO (🔴 Critical)
- Balance between 50-70 ALGO (🟡 Warning)
- Balance exceeds 120 ALGO (ℹ️ Info)

---

## 🔧 Configuration (Optional)

### Change Port (if 5000 is busy)
Edit `app.py`, last line:
```python
app.run(debug=True, host='0.0.0.0', port=8000)  # Change 5000 to 8000
```

### Use Algorand Mainnet
Edit `app.py`, line 75:
```python
ALGOD_ADDRESS = "https://mainnet-api.algonode.cloud"
```

---

## 🚀 Features

✨ **Real-time Monitoring**
- Live balance tracking
- Price updates from Binance
- Market cap from CoinGecko

🎨 **Beautiful Dashboard**
- Dark modern theme
- Responsive design
- Smooth animations

🚨 **Smart Alerts**
- AI-powered risk detection
- Automatic severity levels
- No duplicate alerts (10-minute cooldown)

📊 **Charts & History**
- Price trend visualization
- Balance history tracking
- Last 50 price updates stored

🔐 **Secure**
- Password encryption
- Per-user data isolation
- No private keys stored

---

## 📞 Common Issues

**Q: Port 5000 already in use?**
A: Use a different port (edit app.py, last line)

**Q: No data showing?**
A: Wait 5 seconds after adding address, then refresh

**Q: "Invalid Algorand address"?**
A: Ensure address is exactly 58 characters, starts with a letter

**Q: App crashes?**
A: Delete `instance/algorand_monitor.db` and restart

---

## 📚 File Reference

- `app.py` - Main application
- `requirements.txt` - Dependencies
- `run.bat` - Windows startup script
- `templates/` - HTML pages
- `static/css/` - Styling
- `README.md` - Full documentation

---

## ✅ You're All Set!

Your AlgoGuard AI dashboard is ready to monitor Algorand addresses!

Questions? Check `README.md` for detailed documentation.
