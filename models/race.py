"""
Race model for storing race details and context.
"""
from datetime import datetime
from models import db


class Race(db.Model):
    """Race information model."""
    
    __tablename__ = 'races'
    
    id = db.Column(db.Integer, primary_key=True)
    external_id = db.Column(db.String(100), nullable=True, index=True)  # ID from external API
    meeting = db.Column(db.String(200), nullable=False)  # e.g., "Flemington", "Randwick"
    track = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False, index=True)
    race_number = db.Column(db.Integer, nullable=True)
    race_name = db.Column(db.String(200), nullable=True)
    distance_m = db.Column(db.Integer, nullable=True)  # Distance in meters
    race_class = db.Column(db.String(100), nullable=True)  # e.g., "Maiden", "Handicap", "Listed"
    track_condition = db.Column(db.String(50), nullable=True)  # GOOD, SOFT, HEAVY, SYNTH
    rail_position = db.Column(db.String(50), nullable=True)  # e.g., "True", "+3m"
    num_runners = db.Column(db.Integer, nullable=True)
    source = db.Column(db.String(50), nullable=True)  # "manual", "api", "paste"
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    horses = db.relationship('Horse', backref='race', lazy=True, cascade='all, delete-orphan')
    bets = db.relationship('Bet', backref='race', lazy=True)
    
    def __repr__(self):
        return f'<Race {self.meeting} - {self.date}>'
