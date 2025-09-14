import os
import sqlite3
import sys

# Get the path to the SQLite database file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, 'db.sqlite3')

# Check if the database file exists
if not os.path.exists(db_path):
    print(f"Database file not found at: {db_path}")
    print("Please provide the correct path to your database file:")
    db_path = input().strip()
    if not os.path.exists(db_path):
        print("Database file still not found. Exiting.")
        sys.exit(1)

try:
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if the column already exists
    cursor.execute("PRAGMA table_info(hostel_booking)")
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]
    
    if 'is_paid' not in column_names:
        # Add the is_paid column if it doesn't exist
        print("Adding 'is_paid' column to hostel_booking table...")
        cursor.execute("ALTER TABLE hostel_booking ADD COLUMN is_paid boolean DEFAULT 0")
        conn.commit()
        print("Column added successfully!")
    else:
        print("The 'is_paid' column already exists in the hostel_booking table.")
    
    # Close the connection
    conn.close()
    print("Database connection closed.")
    
except sqlite3.Error as e:
    print(f"SQLite error: {e}")
except Exception as e:
    print(f"An error occurred: {e}")