"""
ClickPunter - Main Flask Application
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from dotenv import load_dotenv
import os
from datetime import date, datetime
import json

# Load environment variables
load_dotenv()

# Import models
from models import db
from models.user import User
from models.race import Race
from models.horse import Horse
from models.bet import Bet

# Import modules
from modules.race_analyzer import analyze_race
from modules.bet_calculator import apply_strategy, estimate_returns, estimate_dividends_from_odds
from modules.form_parser import parse_csv, parse_text, parse_upload
from modules.api_connector import connector

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-me')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///clickpunter.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Routes
@app.route('/')
def index():
    """Home page."""
    recent_races = Race.query.order_by(Race.created_at.desc()).limit(5).all()
    return render_template('index.html', recent_races=recent_races)


@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    """Analyze page for race analysis."""
    if request.method == 'POST':
        return redirect(url_for('index'))
    
    # Get demo race for testing
    demo_race = Race.query.first()
    demo_horses = []
    
    if demo_race:
        demo_horses = Horse.query.filter_by(race_id=demo_race.id).all()
    
    return render_template('analyze.html', demo_race=demo_race, demo_horses=demo_horses)


@app.route('/calculator')
def calculator():
    """Calculator page for betting strategies."""
    return render_template('calculator.html')


@app.route('/history')
@login_required
def history():
    """Betting history page."""
    bets = Bet.query.filter_by(user_id=current_user.id)\
        .join(Race)\
        .order_by(Race.date.desc(), Race.race_number.asc(), Bet.created_at.desc())\
        .all()
    return render_template('history.html', bets=bets)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration."""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if user exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('register'))
        
        if User.query.filter_by(username=username).first():
            flash('Username already taken', 'error')
            return redirect(url_for('register'))
        
        # Create user
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login."""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """User logout."""
    logout_user()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))


# API Routes
@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """Analyze a race and return A/B/C selections."""
    try:
        data = request.get_json()
        race = data.get('race', {})
        horses = data.get('horses', [])
        
        if not horses:
            return jsonify({'error': 'No horses provided'}), 400
        
        # Run analysis
        result = analyze_race(race, horses)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/calc', methods=['POST'])
def api_calc():
    """Calculate betting strategy."""
    try:
        data = request.get_json()
        selections = data.get('selections', {})
        strategy_type = data.get('strategy_type', 'budget_6')
        budget = data.get('budget')
        odds = data.get('odds', {})
        dividends = data.get('dividends', {})
        
        # Apply strategy
        result = apply_strategy(strategy_type, selections, budget=budget)
        
        # If odds provided, estimate dividends
        if odds and 'bets' in result:
            odds_a = odds.get('A') or odds.get('a')
            odds_b = odds.get('B') or odds.get('b')
            odds_c = odds.get('C') or odds.get('c')
            
            if all([odds_a, odds_b, odds_c]):
                estimated_divs = estimate_dividends_from_odds(odds_a, odds_b, odds_c)
                result['estimated_dividends'] = estimated_divs
                
                # Calculate estimated returns
                returns = estimate_returns(result['bets'], estimated_divs)
                result['estimated_returns'] = returns
        
        # Add return estimates if actual dividends provided
        if dividends and 'bets' in result:
            returns = estimate_returns(result['bets'], dividends)
            result['actual_returns'] = returns
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/parse', methods=['POST'])
def api_parse():
    """Parse pasted or uploaded race data."""
    try:
        if 'file' in request.files:
            file = request.files['file']
            horses = parse_upload(file, file.filename)
        else:
            text = request.form.get('text', '')
            
            # Try smart parser first for Racing.com format
            if '\nT:' in text or 'T:\n' in text:
                from modules.smart_parser import smart_parse
                horses = smart_parse(text)
            elif ',' in text and '\n' in text:
                horses = parse_csv(text)
            else:
                horses = parse_text(text)
        
        return jsonify({'horses': horses})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/update-race-details/<int:bet_id>', methods=['POST'])
@login_required
def api_update_race_details(bet_id):
    """Update race details (track and race number) for a bet."""
    try:
        data = request.get_json()
        
        # Get bet and verify ownership
        bet = Bet.query.get(bet_id)
        if not bet or bet.user_id != current_user.id:
            return jsonify({'error': 'Bet not found'}), 404
        
        # Update race details
        race = bet.race
        track = data.get('track', '').strip()
        race_number = data.get('race_number', 0)
        
        race.track = track if track else ''
        race.meeting = track if track else 'Manual Entry'
        race.race_number = race_number
        
        if track:
            race.race_name = f"R{race_number} - {track}" if race_number else track
        else:
            race.race_name = "Manual Bet"
        
        db.session.commit()
        
        return jsonify({'success': True})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/update-bet-result/<int:bet_id>', methods=['POST'])
@login_required
def api_update_bet_result(bet_id):
    """Update bet result after race finishes."""
    try:
        data = request.get_json()
        
        # Get bet and verify ownership
        bet = Bet.query.get(bet_id)
        if not bet or bet.user_id != current_user.id:
            return jsonify({'error': 'Bet not found'}), 404
        
        # Update status
        bet.result_status = data.get('result_status', 'lost')
        bet.updated_at = datetime.now()
        
        db.session.commit()
        
        return jsonify({'success': True})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/delete-bet/<int:bet_id>', methods=['DELETE', 'POST'])
@login_required
def api_delete_bet(bet_id):
    """Delete a bet (user can only delete their own bets)."""
    try:
        # Get bet and verify ownership
        bet = Bet.query.get(bet_id)
        if not bet:
            return jsonify({'success': False, 'error': 'Bet not found'}), 404
        
        if bet.user_id != current_user.id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        # Delete the bet
        db.session.delete(bet)
        db.session.commit()
        
        return jsonify({'success': True}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/save-bet', methods=['POST'])
@login_required
def api_save_bet():
    """Save a bet to history."""
    try:
        data = request.get_json()
        
        # Get or create horses by name
        horse_a_name = data.get('horse_a_name')
        horse_b_name = data.get('horse_b_name')
        horse_c_name = data.get('horse_c_name')
        
        # Get race details from request
        race_track = data.get('race_track', '').strip()
        race_number = data.get('race_number', 0)
        
        # Use empty string if no track provided
        if not race_track:
            race_track = ""
            race_name = "Manual Bet"
        else:
            race_name = f"R{race_number} - {race_track}" if race_number else race_track
        
        # Create race record with provided details
        race = Race(
            meeting=race_track or "Manual Entry",
            track=race_track or "",
            date=date.today(),
            race_name=race_name,
            race_number=race_number if race_number else 0,
            source="calculator"
        )
        db.session.add(race)
        db.session.flush()  # Get race.id
        
        # Create horse records
        horse_a = Horse(race_id=race.id, name=horse_a_name, barrier=0)
        horse_b = Horse(race_id=race.id, name=horse_b_name, barrier=0)
        horse_c = Horse(race_id=race.id, name=horse_c_name, barrier=0)
        
        db.session.add(horse_a)
        db.session.add(horse_b)
        db.session.add(horse_c)
        db.session.flush()  # Get horse IDs
        
        # Get estimated dividends and returns if provided
        estimated_dividends = data.get('estimated_dividends', {})
        estimated_returns = data.get('estimated_returns', {})
        
        # Create bet record
        bet = Bet(
            user_id=current_user.id,
            race_id=race.id,
            a_horse_id=horse_a.id,
            b_horse_id=horse_b.id,
            c_horse_id=horse_c.id,
            stake_total=data.get('stake_total'),
            strategy_type=data.get('strategy_type'),
            breakdown_json=json.dumps(data.get('breakdown', {})),
            est_trifecta_dividend=estimated_dividends.get('trifecta') if estimated_dividends else None,
            est_quinella_dividend=estimated_dividends.get('quinella') if estimated_dividends else None,
            est_trifecta_return=estimated_returns.get('trifecta_return') if estimated_returns else None,
            est_quinella_return=estimated_returns.get('quinella_return') if estimated_returns else None,
            est_total_return=estimated_returns.get('total_return') if estimated_returns else None
        )
        
        db.session.add(bet)
        db.session.commit()
        
        return jsonify({'success': True, 'bet_id': bet.id})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# Error handlers
@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
