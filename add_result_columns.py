"""
Migration script to add result columns to bets table.
Run this once to update existing databases.
"""
import sqlite3
import os

# Determine database path
if os.path.exists('clickpunter.db'):
    db_path = 'clickpunter.db'
elif os.path.exists('/home/ClickPunter/ClickPunter/clickpunter.db'):
    db_path = '/home/ClickPunter/ClickPunter/clickpunter.db'
else:
    print("Database not found!")
    exit(1)

print(f"Using database: {db_path}")

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if columns already exist
cursor.execute("PRAGMA table_info(bets)")
columns = [col[1] for col in cursor.fetchall()]

# Add columns if they don't exist
columns_to_add = [
    ('result_first', 'VARCHAR(100)'),
    ('result_second', 'VARCHAR(100)'),
    ('result_third', 'VARCHAR(100)')
]

for col_name, col_type in columns_to_add:
    if col_name not in columns:
        print(f"Adding column: {col_name}")
        cursor.execute(f"ALTER TABLE bets ADD COLUMN {col_name} {col_type}")
    else:
        print(f"Column {col_name} already exists")

conn.commit()
conn.close()

print("Migration complete!")
