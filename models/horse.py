"""
Horse model for storing runner details and form.
"""
from datetime import datetime
from models import db


class Horse(db.Model):
    """Horse/runner information model."""
    
    __tablename__ = 'horses'
    
    id = db.Column(db.Integer, primary_key=True)
    race_id = db.Column(db.Integer, db.ForeignKey('races.id'), nullable=False, index=True)
    
    # Basic info
    name = db.Column(db.String(100), nullable=False)
    barrier = db.Column(db.Integer, nullable=True)
    odds_decimal = db.Column(db.Float, nullable=True)
    
    # Form and context
    last3_form = db.Column(db.String(50), nullable=True)  # e.g., "12x3" or "x14"
    jockey = db.Column(db.String(100), nullable=True)
    trainer = db.Column(db.String(100), nullable=True)
    
    # Speed map and preferences
    speed_map_hint = db.Column(db.String(20), nullable=True)  # "leaders", "on-pace", "midfield", "back"
    distance_pref = db.Column(db.String(50), nullable=True)  # e.g., "1000-1400m"
    track_pref = db.Column(db.String(200), nullable=True)  # Track names or conditions
    
    # Market data
    market_open_odds = db.Column(db.Float, nullable=True)
    market_current_odds = db.Column(db.Float, nullable=True)
    
    # Status
    is_scratched = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        db.Index('idx_race_name', 'race_id', 'name'),
        db.Index('idx_race_odds', 'race_id', 'odds_decimal'),
    )
    
    def __repr__(self):
        return f'<Horse {self.name} (Barrier {self.barrier})>'
