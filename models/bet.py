"""
Bet model for storing user betting strategies and results.
"""
from datetime import datetime
from models import db


class Bet(db.Model):
    """Bet strategy and results model."""
    
    __tablename__ = 'bets'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    race_id = db.Column(db.Integer, db.ForeignKey('races.id'), nullable=False, index=True)
    
    # Horse selections (A/B/C)
    a_horse_id = db.Column(db.Integer, db.ForeignKey('horses.id'), nullable=True)
    b_horse_id = db.Column(db.Integer, db.ForeignKey('horses.id'), nullable=True)
    c_horse_id = db.Column(db.Integer, db.ForeignKey('horses.id'), nullable=True)
    
    # Betting details
    stake_total = db.Column(db.Float, nullable=False)
    strategy_type = db.Column(db.String(50), nullable=False)  # "budget_5", "budget_6", "custom"
    breakdown_json = db.Column(db.Text, nullable=True)  # JSON string with bet breakdown
    
    # Expected dividends (estimates)
    est_trifecta_dividend = db.Column(db.Float, nullable=True)
    est_quinella_dividend = db.Column(db.Float, nullable=True)
    est_trifecta_return = db.Column(db.Float, nullable=True)  # Your actual return on trifecta
    est_quinella_return = db.Column(db.Float, nullable=True)  # Your actual return on quinella
    est_total_return = db.Column(db.Float, nullable=True)  # Total estimated return
    
    # Results
    result_status = db.Column(db.String(20), default='pending')  # "pending", "won", "lost", "partial"
    result_first = db.Column(db.String(100), nullable=True)  # 1st place horse name
    result_second = db.Column(db.String(100), nullable=True)  # 2nd place horse name
    result_third = db.Column(db.String(100), nullable=True)  # 3rd place horse name
    actual_trifecta_dividend = db.Column(db.Float, nullable=True)
    actual_quinella_dividend = db.Column(db.Float, nullable=True)
    total_return = db.Column(db.Float, nullable=True)
    
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=True, onupdate=datetime.utcnow)
    
    # Relationships to get horse names
    horse_a = db.relationship('Horse', foreign_keys=[a_horse_id], backref='bets_as_a')
    horse_b = db.relationship('Horse', foreign_keys=[b_horse_id], backref='bets_as_b')
    horse_c = db.relationship('Horse', foreign_keys=[c_horse_id], backref='bets_as_c')
    
    def __repr__(self):
        return f'<Bet {self.strategy_type} - ${self.stake_total}>'
