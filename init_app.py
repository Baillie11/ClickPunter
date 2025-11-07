"""
Initialization script for ClickPunter.
Run this before starting the application.
"""
import subprocess
import sys
import os
from datetime import date
import secrets


def install_requirements():
    """Install required packages from requirements.txt."""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✓ Successfully installed required packages\n")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {str(e)}")
        sys.exit(1)


def create_env_file():
    """Create .env file with default configuration."""
    if os.path.exists('.env'):
        print("⚙️  .env file already exists, skipping...\n")
        return
    
    print("📝 Creating .env configuration file...")
    secret_key = secrets.token_hex(32)
    
    env_content = f"""# ClickPunter Configuration
FLASK_ENV=development
SECRET_KEY={secret_key}
DATABASE_URL=sqlite:///clickpunter.db

# API Keys (optional - add your keys here)
ODDS_API_KEY=
BETFAIR_USERNAME=
BETFAIR_PASSWORD=
BETFAIR_APP_KEY=
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✓ Created .env file\n")


def initialize_database():
    """Initialize the database and create tables."""
    print("🗄️  Initializing database...")
    
    try:
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        # Import Flask app to create app context
        from flask import Flask
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///clickpunter.db')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Import models
        from models import db
        from models.user import User
        from models.race import Race
        from models.horse import Horse
        from models.bet import Bet
        
        # Initialize database
        db.init_app(app)
        
        with app.app_context():
            db.create_all()
            print("✓ Database tables created\n")
            
            # Check if we should seed demo data
            seed = input("Seed demo race data? (y/n): ").strip().lower()
            if seed == 'y':
                seed_demo_data(db, Race, Horse)
    
    except Exception as e:
        print(f"❌ Error initializing database: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def seed_demo_data(db, Race, Horse):
    """Seed a demo race with runners."""
    print("🌱 Seeding demo data...")
    
    try:
        # Create demo race
        demo_race = Race(
            meeting='Demo - Flemington',
            track='Flemington',
            date=date.today(),
            race_number=1,
            race_name='Demo Handicap',
            distance_m=1200,
            race_class='Handicap',
            track_condition='GOOD',
            num_runners=9,
            source='manual'
        )
        db.session.add(demo_race)
        db.session.flush()
        
        # Create demo horses
        demo_horses = [
            {
                'name': 'Lightning Fast',
                'barrier': 2,
                'odds_decimal': 3.20,
                'last3_form': '114',
                'jockey': 'J. Smith',
                'trainer': 'T. Brown',
                'speed_map_hint': 'leaders',
                'market_open_odds': 3.50,
                'market_current_odds': 3.20
            },
            {
                'name': 'Steady Runner',
                'barrier': 5,
                'odds_decimal': 6.50,
                'last3_form': '232',
                'jockey': 'K. Jones',
                'trainer': 'P. White',
                'speed_map_hint': 'on-pace'
            },
            {
                'name': 'Value Bet',
                'barrier': 7,
                'odds_decimal': 11.00,
                'last3_form': 'x15 up in trip',
                'jockey': 'M. Davis',
                'trainer': 'R. Green',
                'speed_map_hint': 'midfield'
            },
            {
                'name': 'Back Marker',
                'barrier': 10,
                'odds_decimal': 15.00,
                'last3_form': '45x forgive',
                'jockey': 'S. Williams',
                'trainer': 'L. Black',
                'speed_map_hint': 'back'
            },
            {
                'name': 'Consistent',
                'barrier': 4,
                'odds_decimal': 4.10,
                'last3_form': '223',
                'jockey': 'A. Taylor',
                'trainer': 'M. Johnson',
                'speed_map_hint': 'on-pace'
            },
            {
                'name': 'Long Shot',
                'barrier': 12,
                'odds_decimal': 25.00,
                'last3_form': 'x88',
                'jockey': 'B. Anderson',
                'trainer': 'C. Wilson',
                'speed_map_hint': 'back'
            },
            {
                'name': 'Pace Setter',
                'barrier': 1,
                'odds_decimal': 7.20,
                'last3_form': '341',
                'jockey': 'D. Martin',
                'trainer': 'H. Thompson',
                'speed_map_hint': 'leaders',
                'market_open_odds': 8.00,
                'market_current_odds': 7.20
            },
            {
                'name': 'Mid Pack',
                'barrier': 8,
                'odds_decimal': 13.50,
                'last3_form': 'x34 down in class',
                'jockey': 'E. Harris',
                'trainer': 'J. Lee',
                'speed_map_hint': 'midfield'
            },
            {
                'name': 'Closer',
                'barrier': 9,
                'odds_decimal': 18.00,
                'last3_form': '26x up in trip',
                'jockey': 'F. Clark',
                'trainer': 'K. Moore',
                'speed_map_hint': 'back'
            }
        ]
        
        for horse_data in demo_horses:
            horse = Horse(race_id=demo_race.id, **horse_data)
            db.session.add(horse)
        
        db.session.commit()
        print("✓ Demo data seeded successfully\n")
        print(f"  Race: {demo_race.meeting} - Race {demo_race.race_number}")
        print(f"  Runners: {len(demo_horses)}")
        print()
    
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error seeding demo data: {str(e)}")


def main():
    """Main initialization function."""
    print("\n" + "="*50)
    print("  ClickPunter - Initialization")
    print("="*50 + "\n")
    
    # Install requirements
    install_requirements()
    
    # Create .env file
    create_env_file()
    
    # Initialize database
    initialize_database()
    
    print("="*50)
    print("✅ Initialization complete!")
    print("="*50 + "\n")
    print("Next steps:")
    print("1. (Optional) Edit .env to add API keys")
    print("2. Run: python app.py")
    print("3. Visit: http://127.0.0.1:5000")
    print()
    print("Good luck and bet responsibly! 🍀\n")


if __name__ == "__main__":
    main()
