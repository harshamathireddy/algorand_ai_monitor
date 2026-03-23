# AlgoGuard AI - Algorand Blockchain Monitoring Dashboard

A modern, real-time monitoring dashboard for Algorand blockchain accounts with AI-powered risk detection and alerts.

## Features

✅ **Real-time Monitoring**
- Live Algorand account balance tracking
- Blockchain round number monitoring
- Price updates from Binance API

✅ **Market Analytics**
- Real-time ALGO price tracking (USD)
- Market cap monitoring from CoinGecko
- Price history charts with Chart.js

✅ **AI-Powered Alerts**
- Automatic risk scoring based on balance
- Intelligent alert generation
- Severity levels: Info, Warning, Critical

✅ **User Management**
- Secure registration and login
- Password hashing with Werkzeug
- Per-user account isolation

✅ **Modern UI**
- Dark theme with cyan/green accents
- Responsive design (desktop & mobile)
- Real-time data updates via JavaScript

## Tech Stack

- **Backend**: Flask 2.3.3
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: Flask-Login with password hashing
- **Blockchain**: Algorand SDK
- **APIs**: Binance, CoinGecko
- **Frontend**: HTML, CSS, Chart.js

## Installation

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Quick Start (Windows)

1. **Clone or download the project**
   ```bash
   cd algorand_ai_monitor
   ```

2. **Run the startup script**
   ```bash
   run.bat
   ```
   
   This will:
   - Install all dependencies
   - Create the SQLite database
   - Start the Flask application

3. **Open in browser**
   ```
   http://localhost:5000
   ```

### Manual Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application**
   ```bash
   python app.py
   ```

3. **Access the dashboard**
   ```
   http://localhost:5000
   ```

## Usage

### Getting Started

1. **Create an Account**
   - Click "Register" on the login page
   - Enter username, email, and password
   - Confirm your password and submit

2. **Configure Algorand Address**
   - Log in to your account
   - Go to "Settings"
   - Enter your 58-character Algorand address
   - Click "Save Algorand Address"
   - Monitoring will start automatically

3. **View Dashboard**
   - Navigate to "Dashboard"
   - See real-time balance, price, and market data
   - View AI alerts and balance history
   - Check price charts

### Algorand Address Format

A valid Algorand address:
- Is exactly **58 characters** long
- Starts with a letter (A-Z)
- Uses base32 encoding

**Example**: `M5VOM4OO5PC54SDVXPSPKLZCTACLSZBA4H3LLCSWPK25KV42YZFMFGV4UU`

## API Endpoints

### Authentication
- `GET /` - Redirect to dashboard or login
- `POST /register` - Create new account
- `POST /login` - User login
- `GET /logout` - User logout

### Dashboard
- `GET /dashboard` - Main dashboard page
- `GET /settings` - Settings page
- `POST /settings` - Update Algorand address

### Data APIs
- `GET /api/user-status` - Get current user monitoring data
- `GET /api/price-history` - Get price history for charts

### Error Handling
- `GET /404` - Page not found
- `GET /500` - Server error

## Configuration

### Environment Variables

The app uses default settings. For production, modify `app.py`:

```python
# Change this to a secure random string
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'

# Change database URI if needed (default: SQLite)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///algorand_monitor.db'
```

### Blockchain Endpoints

Default: Algorand Testnet via AlgoNode (free public API)
```python
ALGOD_ADDRESS = "https://testnet-api.algonode.cloud"
```

To use mainnet:
```python
ALGOD_ADDRESS = "https://mainnet-api.algonode.cloud"
```

## Data Sources

- **Blockchain Data**: Algorand Testnet/Mainnet via AlgoNode
- **Price Data**: Binance API (ALGOUSDT pair)
- **Market Cap**: CoinGecko API
- **Local Storage**: SQLite database (algorand_monitor.db)

## Database Schema

### Users
- Username (unique)
- Email (unique)
- Password hash
- Algorand address
- Monitoring status
- Creation timestamp

### Monitoring Data
- User balance
- Price
- Market cap
- Risk score
- Blockchain round
- Timestamp

### Alerts
- Alert message
- Severity level
- Timestamp

### Price History
- Price per ALGO
- Market cap
- Timestamp

## Risk Scoring

The AI generates risk scores based on balance levels:

| Balance | Risk Score | Status |
|---------|-----------|--------|
| < 50 ALGO | 75 | 🔴 High Risk |
| 50-70 ALGO | 50 | 🟡 Warning |
| 70-120 ALGO | 40 | 🟢 Safe |
| > 120 ALGO | 20 | 🟢 Very Safe |

## Alert Types

### Critical Alerts (Balance < 50 ALGO)
```
⚠️ Critical: Balance very low at X.XX ALGO
```

### Warning Alerts (Balance 50-70 ALGO)
```
⚠️ Warning: Balance low at X.XX ALGO
```

### Info Alerts (Balance > 120 ALGO)
```
ℹ️ Info: High balance detected X.XX ALGO
```

## Security Features

✅ Passwords hashed using Werkzeug
✅ Per-user data isolation
✅ No private keys stored
✅ Read-only blockchain access
✅ CSRF protection via Flask-Login
✅ Secure session management

## Background Monitoring

The application runs a daemon thread that:
- Updates Algorand prices every 30 seconds
- Monitors all active users' addresses
- Creates alerts based on balance changes
- Maintains price history
- Cleans up old data (keeps last 50 price entries per user)

## Troubleshooting

### Port Already in Use
If port 5000 is already in use, modify `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=8000)  # Use port 8000
```

### Database Issues
Delete the database and restart:
```bash
del instance\algorand_monitor.db
python app.py
```

### Blockchain Connection Error
- Check internet connection
- Verify AlgoNode API is accessible
- Check Algorand address validity (58 characters)

### No Data Appearing
- Ensure Algorand address is configured in Settings
- Check if address has ALGO balance
- Wait 5+ seconds for first data collection
- Check browser console for JavaScript errors

## File Structure

```
algorand_ai_monitor/
├── app.py                    # Main Flask application
├── requirements.txt          # Python dependencies
├── run.bat                   # Windows startup script
├── README.md                 # This file
├── templates/                # HTML templates
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── settings.html
│   ├── 404.html
│   └── 500.html
├── static/                   # Static assets
│   └── css/
│       ├── auth.css         # Authentication pages styling
│       └── style.css        # Dashboard styling
└── instance/                # Runtime data (auto-created)
    └── algorand_monitor.db  # SQLite database
```

## Performance

- **Database**: SQLite (suitable for personal/small team use)
- **Polling Interval**: 5 seconds (monitoring loop)
- **Price Update**: 30 seconds (cached)
- **Dashboard Refresh**: 3 seconds (client-side)
- **Data Retention**: Last 50 price entries per user

For larger deployments, consider:
- PostgreSQL instead of SQLite
- Redis for caching
- Celery for background tasks

## Development

### Running in Debug Mode
The app runs with `debug=True` by default for development.

### Making Changes
1. Edit source files
2. The Flask development server auto-reloads
3. Refresh browser to see changes

### Database Migrations
For schema changes, delete the database and restart:
```bash
del instance\algorand_monitor.db
python app.py
```

## Deployment

For production:

1. **Change secret key**
   ```python
   app.config['SECRET_KEY'] = 'your-production-secret-key'
   ```

2. **Use production database**
   - PostgreSQL recommended
   ```python
   app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://...'
   ```

3. **Disable debug mode**
   ```python
   app.run(debug=False, host='0.0.0.0', port=5000)
   ```

4. **Use production server**
   - Gunicorn: `gunicorn -w 4 app:app`
   - Waitress: `waitress-serve --port=5000 app:app`

## License

This project is provided as-is for educational and personal use.

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Verify Algorand address format
3. Check internet connectivity
4. Review browser console for errors
5. Check application logs

## Disclaimer

This application monitors public blockchain data. It does not store or access private keys. Always keep your private keys secure and never share them with anyone.

---

**Made with ❤️ for Algorand enthusiasts**
