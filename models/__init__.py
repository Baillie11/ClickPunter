"""
Database models for ClickPunter.
"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from models.user import User
from models.race import Race
from models.horse import Horse
from models.bet import Bet

__all__ = ['db', 'User', 'Race', 'Horse', 'Bet']
