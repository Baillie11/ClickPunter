# 🏇 ClickPunter - ABC Method Horse Racing Assistant

Just for shits and giggles I built a horse race predictor based on the ABC Method betting strategy. This little Flask app analyzes horse races and picks three horses: an Anchor (A) at $2.50-$4.50 odds, a Pace horse (B) at $5-$10, and a Value pick (C) at $8-$18. It then calculates boxed trifecta and quinella bets using various strategies ($5, $6, $10, $15 budgets).

The app can parse messy race data from Racing.com, automatically suggest your A/B/C selections based on form, barriers, and market moves, and estimate potential payouts using fixed odds. You can save your bets, track your history, and see if your tips would've won by entering race results.

## ⚠️ Important Disclaimers

- This app is **100% UNTESTED** in real-world betting scenarios
- The ABC Method is a betting strategy, not a guaranteed winning system
- Estimated payouts are rough approximations and will differ from actual TAB dividends
- **Please gamble responsibly and never bet more than you can afford to lose**
- This is a hobby project built for fun and learning - use at your own risk!

🍀 **Bet responsibly. Know when to stop.**

## Features

- 🏇 **Race Analysis**: Automatically identifies A/B/C horses based on form, odds, barriers, and conditions
- 💰 **Betting Calculator**: Calculates boxed trifecta and quinella stakes with flexi options
- 📊 **History Tracking**: Save and review past bets with results tracking
- 📝 **Multiple Input Methods**:
  - Manual entry
  - Paste/upload race cards (CSV or text)
  - API integration (The Odds API, Betfair)
- ✅ **Quick Checklist**: Validates race conditions (field size, barriers, track conditions, market firmers)
- 🎯 **Multiple Strategies**:
  - **$5 Budget**: $2 flexi trifecta + $3 quinella
  - **$6 Budget**: $0.50 trifecta box + $1.00 quinella box
  - **$10 Budget**: $1 trifecta box + $4 quinella box
  - **$15 Budget**: $1.50 trifecta box + $6 quinella box
  - **Trifecta Only**: $1 trifecta box ($6 total)
  - **Quinella Only**: $2 quinella box ($6 total)
  - **Custom**: Define your own budget split
- 💰 **Payout Estimator**: Calculate potential returns based on fixed odds (20% takeout)
- 📝 **TAB Instructions**: Hover over strategy names to see exactly how to place bets at TAB
- ✏️ **Editable History**: Update race details and enter results after races finish

## Tech Stack

- **Backend**: Python 3.11 + Flask
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Database**: SQLite + SQLAlchemy ORM
- **Authentication**: Flask-Login
- **Forms**: Flask-WTF with CSRF protection

## Installation

### Prerequisites

- Python 3.11+
- pip

### Setup

1. **Clone or navigate to the project directory**:
   ```powershell
   cd C:\Users\andre\OneDrive\Projects\flask\ClickPunter
   ```

2. **Create and activate virtual environment**:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\activate
   ```

3. **Run initialization script**:
   ```powershell
   python init_app.py
   ```
   This will:
   - Install all dependencies
   - Create `.env` file with configuration
   - Initialize the database
   - Optionally seed demo data

4. **Configure API keys** (optional):
   Edit `.env` and add your API keys:
   ```
   ODDS_API_KEY=your_key_here
   BETFAIR_USERNAME=your_username
   BETFAIR_PASSWORD=your_password
   BETFAIR_APP_KEY=your_app_key
   ```

5. **Run the application**:
   ```powershell
   python app.py
   ```

6. **Open in browser**:
   Navigate to `http://127.0.0.1:5000`

## Usage

### Quick Start

1. **Create an account** (Register/Login)
2. **Navigate to Analyze** to input race data
3. **Enter horses** via:
   - Manual entry form
   - Paste text (e.g., "1. Horse Name (B3) $4.50 J:Smith T:Brown 12x")
   - Upload CSV file
   - Import from API (if configured)
4. **Run Analysis** to see A/B/C selections and checklist
5. **Go to Calculator** with your selections
6. **Choose strategy** ($5, $6, or custom)
7. **Save Bet** to track results

### CSV Format Example

Create `sample_race.csv`:
```csv
name,barrier,odds,last3_form,jockey,trainer,speed_map_hint
Fast Horse,3,3.50,12x,J. Smith,T. Brown,leaders
Mid Runner,7,6.00,234,K. Jones,P. White,on-pace
Value Pick,5,12.00,x15 up in trip,M. Davis,R. Green,midfield
```

### Text Format Example

```
1. Fast Horse (3) $3.50 J:Smith T:Brown 12x
2. Mid Runner (7) $6.00 J:Jones T:White 234
3. Value Pick (5) $12.00 J:Davis T:Green x15 up in trip
```

## Project Structure

```
ClickPunter/
├── app.py                   # Main Flask application
├── init_app.py             # Initialization script
├── requirements.txt         # Python dependencies
├── .env                     # Configuration (created by init_app.py)
├── README.md               # This file
├── models/                  # Database models
│   ├── user.py
│   ├── race.py
│   ├── horse.py
│   └── bet.py
├── modules/                 # Core business logic
│   ├── race_analyzer.py    # ABC selection engine
│   ├── bet_calculator.py   # Betting calculations
│   ├── api_connector.py    # External API integration
│   └── form_parser.py      # Data parsing
├── utils/                   # Helper functions
│   ├── odds_helpers.py
│   └── validators.py
├── auth/                    # Authentication
│   ├── routes.py
│   └── forms.py
├── templates/               # HTML templates
│   ├── layout.html
│   ├── index.html
│   ├── analyze.html
│   ├── calculator.html
│   └── history.html
└── static/                  # CSS, JS, images
    ├── css/
    ├── js/
    └── img/
```

## ABC Method Explained

### Anchor (A)
- **Odds Range**: $2.80 - $4.50
- **Criteria**: Best credentialed runner with:
  - Barrier ≤ 10 (preferred)
  - At least 2 top-4 finishes in last 3 runs
  - Track/distance suitability
  - Market support (firming odds)

### Pace/Position (B)
- **Odds Range**: $5.00 - $10.00
- **Criteria**: On-speed runner with:
  - Speed map position: Leaders or on-pace
  - Barrier ≤ 8 (preferred)
  - Proven at today's distance
  - Soft run expected

### Value (C)
- **Odds Range**: $8.00 - $18.00
- **Criteria**: Ready to spike with:
  - Up in trip (distance increase)
  - Down in class
  - Forgive last run (excuse)
  - Strong late sectionals

### The Quick Checklist
- ✅ Field size 8-12 runners (sweet spot)
- ✅ A and B have barriers 1-8
- ✅ Track condition suits (wet form if wet track)
- ✅ Market firmers (A/B shortening in odds)

## Betting Strategies

### $6 Strategy
- **Trifecta Boxed**: 6 combos @ $0.50 = $3.00
- **Quinella Boxed**: 3 combos @ $1.00 = $3.00
- **Total**: $6.00
- **Returns**: Full dividend if hit

### $5 Strategy (Flexi)
- **Trifecta Boxed (Flexi)**: $2.00 (33.33% of dividend)
- **Quinella Boxed**: 3 combos @ $1.00 = $3.00
- **Total**: $5.00
- **Returns**: Flexi trifecta + full quinella

### Custom Strategy
- Set your own budget
- Adjust trifecta/quinella split
- Auto-calculates flexi percentages

## API Integration

### The Odds API
Set `ODDS_API_KEY` in `.env` to enable:
- Live race meetings
- Current odds
- Market movements

### Betfair API
Set credentials in `.env` to enable:
- Market book data
- Live price updates

## Development

### Running Tests
```powershell
pytest
```

### Database Migrations
```powershell
# Future: Add Flask-Migrate
flask db migrate -m "description"
flask db upgrade
```

## Future Enhancements

- [ ] Advanced pace mapping visualization
- [ ] Multi-race bet builder
- [ ] PDF/CSV export of bets
- [ ] ROI analytics and statistics
- [ ] Mobile app version
- [ ] Real-time odds tracking
- [ ] Social features (share tips)

## License

MIT License - Use at your own risk!

## Support

⚠️ **This is NOT financial advice. Gamble responsibly.**

For more information on responsible gambling:
- Gambling Help Online: https://www.gamblinghelponline.org.au
- Phone: 1800 858 858

---

**Good luck and bet responsibly!** 🍀
