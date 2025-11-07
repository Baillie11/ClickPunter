"""
Add estimated return columns to bets table.
Run this once to update the database schema.
"""
from app import app, db
from sqlalchemy import text

with app.app_context():
    try:
        # Add the new columns to the bets table
        with db.engine.connect() as conn:
            conn.execute(text('ALTER TABLE bets ADD COLUMN est_trifecta_return FLOAT'))
            conn.execute(text('ALTER TABLE bets ADD COLUMN est_quinella_return FLOAT'))
            conn.execute(text('ALTER TABLE bets ADD COLUMN est_total_return FLOAT'))
            conn.commit()
        
        print("✅ Successfully added est_trifecta_return, est_quinella_return, and est_total_return columns to bets table!")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Note: If columns already exist, this is expected.")
