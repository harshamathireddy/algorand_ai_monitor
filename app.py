from flask import Flask, render_template, jsonify, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from algosdk.v2client import algod
import threading
import time
import requests
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///algorand_monitor.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize Extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# --- DATABASE MODELS ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    algo_address = db.Column(db.String(58), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    monitoring_enabled = db.Column(db.Boolean, default=True)
    
    # Relationship
    monitoring_data = db.relationship('UserMonitoringData', backref='user', lazy=True, cascade='all, delete-orphan')
    price_history = db.relationship('PriceHistory', backref='user', lazy=True, cascade='all, delete-orphan')
    alerts = db.relationship('Alert', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class UserMonitoringData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    round = db.Column(db.Integer, default=0)
    algo_balance = db.Column(db.Float, default=0.0)
    algo_price = db.Column(db.Float, default=0.0)
    market_cap = db.Column(db.Float, default=0.0)
    balance_value_usd = db.Column(db.Float, default=0.0)
    risk_score = db.Column(db.Integer, default=0)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class PriceHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    price = db.Column(db.Float, default=0.0)
    market_cap = db.Column(db.Float, default=0.0)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    severity = db.Column(db.String(20), default='Info')  # Info, Warning, High
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- ALGORAND CONFIG ---
ALGOD_ADDRESS = "https://testnet-api.algonode.cloud"
ALGOD_TOKEN = ""
algod_client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)

# Global state for monitoring all users
monitoring_active = True
last_price_update = {}

def run_ai_monitor():
    """Background task to monitor all users' Algorand addresses."""
    global last_price_update
    price_update_interval = 30
    
    while monitoring_active:
        try:
            # Get current ALGO price and market cap (once for all users)
            current_time = time.time()
            cache_key = "global_price"
            
            if cache_key not in last_price_update or current_time - last_price_update[cache_key] > price_update_interval:
                try:
                    # Get price from Binance
                    binance_response = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=ALGOUSDT", timeout=10)
                    binance_response.raise_for_status()
                    binance_data = binance_response.json()
                    global_price = float(binance_data.get("price", 0.25))
                    print(f"✓ Binance Price: ${global_price:.4f}")
                except Exception as e:
                    global_price = 0.25
                    print(f"⚠ Price fetch failed: {e}")
                
                try:
                    # Get market cap from CoinGecko
                    cg_response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=algorand&vs_currencies=usd&include_market_cap=true", timeout=10)
                    cg_response.raise_for_status()
                    cg_data = cg_response.json()
                    global_market_cap = cg_data.get("algorand", {}).get("usd_market_cap", 10000000000)
                    print(f"✓ Market Cap: ${global_market_cap:.0f}")
                except Exception as e:
                    global_market_cap = 10000000000
                    print(f"⚠ Market cap fetch failed: {e}")
                
                last_price_update[cache_key] = current_time
            else:
                # Use cached values
                global_price = 0.25
                global_market_cap = 10000000000
            
            # Monitor each active user
            with app.app_context():
                active_users = User.query.filter_by(monitoring_enabled=True).all()
                
                for user in active_users:
                    if not user.algo_address:
                        continue
                    
                    try:
                        # Get blockchain data for this user
                        status = algod_client.status()
                        round_num = status.get("last-round")
                        
                        info = algod_client.account_info(user.algo_address)
                        algo_balance = info.get('amount') / 1_000_000
                        balance_usd = algo_balance * global_price
                        
                        # Save monitoring data
                        monitoring = UserMonitoringData(
                            user_id=user.id,
                            round=round_num,
                            algo_balance=algo_balance,
                            algo_price=global_price,
                            market_cap=global_market_cap,
                            balance_value_usd=balance_usd,
                            risk_score=calculate_risk_score(algo_balance)
                        )
                        db.session.add(monitoring)
                        
                        # Save price history
                        price_hist = PriceHistory(
                            user_id=user.id,
                            price=global_price,
                            market_cap=global_market_cap
                        )
                        db.session.add(price_hist)
                        
                        # Check for alerts
                        check_and_create_alerts(user.id, algo_balance, global_price)
                        
                        # Keep only last 50 price history entries per user
                        old_prices = PriceHistory.query.filter_by(user_id=user.id).order_by(PriceHistory.timestamp.asc()).offset(50).all()
                        for old in old_prices:
                            db.session.delete(old)
                        
                        db.session.commit()
                        print(f"✓ Updated {user.username}: {algo_balance:.2f} ALGO (${balance_usd:.2f})")
                        
                    except Exception as e:
                        print(f"✗ Error monitoring user {user.username}: {e}")
                        db.session.rollback()
        
        except Exception as e:
            print(f"Monitoring error: {e}")
        
        time.sleep(5)

def calculate_risk_score(balance):
    """Calculate risk score based on balance."""
    if balance < 50:
        return 75
    elif balance < 70:
        return 50
    elif balance > 120:
        return 20
    else:
        return 40

def check_and_create_alerts(user_id, balance, price):
    """Check balance and create alerts if needed."""
    # Check if identical alert exists in last 10 minutes
    ten_min_ago = datetime.utcnow() - timedelta(minutes=10)
    
    if balance < 50:
        msg = f"Critical: Balance very low at {balance:.2f} ALGO"
        existing = Alert.query.filter_by(user_id=user_id).filter(Alert.message == msg).filter(Alert.timestamp > ten_min_ago).first()
        if not existing:
            alert = Alert(user_id=user_id, message=msg, severity='High')
            db.session.add(alert)
    elif balance < 70:
        msg = f"Warning: Balance low at {balance:.2f} ALGO"
        existing = Alert.query.filter_by(user_id=user_id).filter(Alert.message == msg).filter(Alert.timestamp > ten_min_ago).first()
        if not existing:
            alert = Alert(user_id=user_id, message=msg, severity='Warning')
            db.session.add(alert)
    elif balance > 120:
        msg = f"Info: High balance detected {balance:.2f} ALGO"
        existing = Alert.query.filter_by(user_id=user_id).filter(Alert.message == msg).filter(Alert.timestamp > ten_min_ago).first()
        if not existing:
            alert = Alert(user_id=user_id, message=msg, severity='Info')
            db.session.add(alert)

# Start monitoring thread
monitoring_thread = threading.Thread(target=run_ai_monitor, daemon=True)
monitoring_thread.start()

# --- ROUTES ---

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        
        # Validation
        if not username or not email or not password:
            return render_template('register.html', error='All fields required'), 400
        
        if password != confirm:
            return render_template('register.html', error='Passwords do not match'), 400
        
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error='Username already exists'), 400
        
        if User.query.filter_by(email=email).first():
            return render_template('register.html', error='Email already exists'), 400
        
        # Create user
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid username or password'), 401
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        algo_address = request.form.get('algo_address')
        
        if algo_address and len(algo_address) == 58:
            current_user.algo_address = algo_address
            db.session.commit()
            return render_template('settings.html', user=current_user, success='Algorand address updated')
        else:
            return render_template('settings.html', user=current_user, error='Invalid Algorand address'), 400
    
    return render_template('settings.html', user=current_user)

@app.route('/exchange')
@login_required
def exchange():
    """View ALGO exchange rates in different currencies."""
    return render_template('exchange.html', user=current_user)

@app.route('/api/user-status')
@app.route('/api/status')
@login_required
def user_status():
    """Get current user's monitoring data."""
    if not current_user.algo_address:
        return jsonify({
            'error': 'No Algorand address configured',
            'round': 0,
            'algo_balance': 0,
            'algo_price': 0,
            'market_cap': 0,
            'balance_value_usd': 0,
            'risk_score': 0,
            'alerts': [],
            'history': [],
            'price_history': []
        })
    
    # Get latest monitoring data
    latest = UserMonitoringData.query.filter_by(user_id=current_user.id).order_by(UserMonitoringData.timestamp.desc()).first()
    
    # Get recent alerts
    recent_alerts = Alert.query.filter_by(user_id=current_user.id).order_by(Alert.timestamp.desc()).limit(10).all()
    alerts_data = [
        {
            'id': a.id,
            'msg': a.message,
            'severity': a.severity,
            'timestamp': a.timestamp.timestamp()
        }
        for a in recent_alerts
    ]
    
    # Get balance history
    history = UserMonitoringData.query.filter_by(user_id=current_user.id).order_by(UserMonitoringData.timestamp.desc()).limit(20).all()
    history_data = [
        {
            'timestamp': h.timestamp.timestamp(),
            'balance': h.algo_balance,
            'price': h.algo_price
        }
        for h in reversed(history)
    ]

    # Get price history
    price_history = PriceHistory.query.filter_by(user_id=current_user.id).order_by(PriceHistory.timestamp.asc()).limit(50).all()
    price_history_data = [
        {
            'timestamp': p.timestamp.timestamp(),
            'price': p.price,
            'market_cap': p.market_cap
        }
        for p in price_history
    ]
    
    if latest:
        return jsonify({
            'round': latest.round,
            'algo_balance': latest.algo_balance,
            'algo_price': latest.algo_price,
            'market_cap': latest.market_cap,
            'balance_value_usd': latest.balance_value_usd,
            'risk_score': latest.risk_score,
            'alerts': alerts_data,
            'history': history_data,
            'price_history': price_history_data
        })
    else:
        return jsonify({
            'round': 0,
            'algo_balance': 0,
            'algo_price': 0,
            'market_cap': 0,
            'balance_value_usd': 0,
            'risk_score': 0,
            'alerts': [],
            'history': [],
            'price_history': []
        })

@app.route('/api/price-history')
@login_required
def price_history():
    """Get price history for chart."""
    prices = PriceHistory.query.filter_by(user_id=current_user.id).order_by(PriceHistory.timestamp.asc()).limit(50).all()
    data = [
        {
            'timestamp': p.timestamp.timestamp(),
            'price': p.price,
            'market_cap': p.market_cap
        }
        for p in prices
    ]
    return jsonify(data)

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)