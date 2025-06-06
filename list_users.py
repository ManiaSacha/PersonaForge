import sqlite3
import json
from pathlib import Path

# Connect to the database
conn = sqlite3.connect('personaforge.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# List all tables in the database
print("=== DATABASE TABLES ===")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
for table in tables:
    print(f"Table: {table['name']}")
    # Show schema for each table
    cursor.execute(f"PRAGMA table_info({table['name']})")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  - {col['name']} ({col['type']})")
    print()

# Try to query each table
for table in tables:
    table_name = table['name']
    print(f"\n=== CONTENTS OF {table_name.upper()} ===")
    try:
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
        rows = cursor.fetchall()
        if rows:
            # Print column names
            print("| " + " | ".join(dict(rows[0]).keys()) + " |")
            print("|" + "-|" * len(dict(rows[0])))
            
            # Print data
            for row in rows:
                row_dict = dict(row)
                print("| " + " | ".join(str(val) for val in row_dict.values()) + " |")
        else:
            print(f"No data in {table_name}")
    except sqlite3.Error as e:
        print(f"Error querying {table_name}: {e}")


# Check JSON files
print("\n=== PERSONA JSON FILES ===")
persona_dir = Path("backend/persona_profiles")
for file in persona_dir.glob("*.json"):
    if file.name.endswith(".bak.json"):
        continue
    with open(file) as f:
        try:
            data = json.load(f)
            user_id = data.get("user_id", "No user ID")
            print(f"File: {file.name}, Name: {data.get('name')}, User ID: {user_id}")
        except json.JSONDecodeError:
            print(f"Error reading {file.name}")

conn.close()
