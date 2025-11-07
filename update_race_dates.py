"""
Script to update race dates to today's date.
Run this in PythonAnywhere Bash console from your app directory.
"""
import os
import sys
from datetime import date

# Set DATABASE_URL if not already set (for PythonAnywhere)
if 'DATABASE_URL' not in os.environ:
    # Default to looking for database in current directory
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'clickpunter.db')
    if not os.path.exists(db_path):
        # Check common PythonAnywhere location
        db_path = '/home/ClickPunter/ClickPunter/clickpunter.db'
    os.environ['DATABASE_URL'] = f'sqlite:///{db_path}'
    print(f"Using database: {db_path}")

from app import app
from models import db
from models.race import Race

def update_race_dates():
    with app.app_context():
        try:
            # Get all races with date 2025-11-07
            races = Race.query.filter_by(date=date(2025, 11, 7)).all()
            
            print(f"Found {len(races)} race(s) with date 07/11/2025")
            
            if not races:
                print("No races found to update.")
                return
            
            # Display races before update
            print("\nRaces to update:")
            for race in races:
                print(f"  - ID: {race.id}, Meeting: {race.meeting}, Track: {race.track}, Date: {race.date}")
            
            # Ask for confirmation
            confirm = input("\nUpdate these race dates to today? (yes/no): ")
            
            if confirm.lower() in ['yes', 'y']:
                today = date.today()
                for race in races:
                    race.date = today
                
                db.session.commit()
                print(f"\n✅ Updated {len(races)} race(s) to {today.strftime('%d/%m/%Y')}")
            else:
                print("Update cancelled.")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print(f"\nCurrent DATABASE_URL: {app.config['SQLALCHEMY_DATABASE_URI']}")
            print("\nPlease check that the database file exists and is accessible.")
            sys.exit(1)

if __name__ == '__main__':
    update_race_dates()
