import sqlite3
import argparse
import json
from tabulate import tabulate
from pathlib import Path

def connect_db(db_path="personaforge.db"):
    """Connect to the database and return connection and cursor."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    return conn, cursor

def list_tables(cursor):
    """List all tables in the database."""
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("\n=== DATABASE TABLES ===")
    for table in tables:
        print(f"Table: {table['name']}")
        # Show schema for each table
        cursor.execute(f"PRAGMA table_info({table['name']})")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  - {col['name']} ({col['type']})")
        print()
    return [table['name'] for table in tables]

def run_query(cursor, query):
    """Run a SQL query and display results."""
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        if not rows:
            print("Query returned no results.")
            return
        
        # Convert to list of dicts for tabulate
        headers = list(dict(rows[0]).keys())
        table_data = [list(dict(row).values()) for row in rows]
        
        # Print as a nice table
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        print(f"Total rows: {len(rows)}")
    except sqlite3.Error as e:
        print(f"Error executing query: {e}")

def show_table(cursor, table_name, limit=10):
    """Show contents of a table."""
    try:
        cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
        rows = cursor.fetchall()
        if not rows:
            print(f"Table '{table_name}' is empty.")
            return
        
        # Convert to list of dicts for tabulate
        headers = list(dict(rows[0]).keys())
        table_data = [list(dict(row).values()) for row in rows]
        
        # Print as a nice table
        print(f"\n=== CONTENTS OF {table_name.upper()} (LIMIT {limit}) ===")
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        
        # Get total count
        cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
        count = cursor.fetchone()['count']
        print(f"Showing {len(rows)} of {count} total rows")
    except sqlite3.Error as e:
        print(f"Error querying {table_name}: {e}")

def check_persona_files():
    """Check persona JSON files for user_id field."""
    print("\n=== PERSONA JSON FILES ===")
    persona_dir = Path("backend/persona_profiles")
    files = list(persona_dir.glob("*.json"))
    
    if not files:
        print("No persona files found.")
        return
    
    file_data = []
    for file in files:
        if file.name.endswith(".bak.json"):
            continue
        try:
            with open(file) as f:
                data = json.load(f)
                user_id = data.get("user_id", "None")
                file_data.append({
                    "File": file.name,
                    "Name": data.get("name", "Unknown"),
                    "User ID": user_id
                })
        except json.JSONDecodeError:
            file_data.append({
                "File": file.name,
                "Name": "ERROR",
                "User ID": "ERROR"
            })
    
    print(tabulate(file_data, headers="keys", tablefmt="grid"))

def update_persona_user_id(user_id):
    """Update all persona files to include the specified user_id."""
    persona_dir = Path("backend/persona_profiles")
    updated = 0
    
    for file in persona_dir.glob("*.json"):
        if file.name.endswith(".bak.json"):
            continue
        try:
            with open(file) as f:
                data = json.load(f)
            
            # Skip if already has user_id
            if "user_id" in data and data["user_id"] == user_id:
                continue
                
            # Add user_id
            data["user_id"] = user_id
            
            # Save backup
            backup = file.with_name(f"{file.stem}.bak.json")
            with open(backup, 'w') as f:
                json.dump(data, f, indent=2)
                
            # Save updated file
            with open(file, 'w') as f:
                json.dump(data, f, indent=2)
                
            updated += 1
            print(f"Updated {file.name} with user_id: {user_id}")
        except Exception as e:
            print(f"Error updating {file.name}: {e}")
    
    print(f"\nTotal files updated: {updated}")

def main():
    parser = argparse.ArgumentParser(description="Query the PersonaForge database")
    parser.add_argument("--list-tables", action="store_true", help="List all tables in the database")
    parser.add_argument("--show-table", type=str, help="Show contents of a specific table")
    parser.add_argument("--limit", type=int, default=10, help="Limit number of rows returned")
    parser.add_argument("--query", type=str, help="Run a custom SQL query")
    parser.add_argument("--check-files", action="store_true", help="Check persona JSON files")
    parser.add_argument("--update-user-id", type=str, help="Update all persona files with this user_id")
    
    args = parser.parse_args()
    conn, cursor = connect_db()
    
    if args.list_tables:
        list_tables(cursor)
    elif args.show_table:
        show_table(cursor, args.show_table, args.limit)
    elif args.query:
        run_query(cursor, args.query)
    elif args.check_files:
        check_persona_files()
    elif args.update_user_id:
        update_persona_user_id(args.update_user_id)
    else:
        # Default: show all tables and their contents
        tables = list_tables(cursor)
        for table in tables:
            show_table(cursor, table, args.limit)
        check_persona_files()
    
    conn.close()

if __name__ == "__main__":
    main()
