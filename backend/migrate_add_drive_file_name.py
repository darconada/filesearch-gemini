"""Migration script to add drive_file_name column to drive_links table"""
import sqlite3
from pathlib import Path

# Database path
db_path = Path(__file__).parent / "app.db"

if not db_path.exists():
    print(f"Database not found at {db_path}")
    print("The column will be created when the database is initialized.")
    exit(0)

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if column already exists
cursor.execute("PRAGMA table_info(drive_links)")
columns = [col[1] for col in cursor.fetchall()]

if 'drive_file_name' in columns:
    print("Column 'drive_file_name' already exists. Migration not needed.")
else:
    print("Adding 'drive_file_name' column to drive_links table...")
    cursor.execute("ALTER TABLE drive_links ADD COLUMN drive_file_name VARCHAR")
    conn.commit()
    print("✅ Migration completed successfully!")

conn.close()
