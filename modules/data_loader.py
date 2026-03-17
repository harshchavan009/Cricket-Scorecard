import sqlite3
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'data/ipl_data.sqlite')

def load_data(table_name):
    """Load data from SQLite database."""
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}. Please run scraper.py first.")
        return pd.DataFrame()
        
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
        conn.close()
        return df
    except Exception as e:
        print(f"Error loading {table_name}: {e}")
        return pd.DataFrame()

def load_team_stats():
    return load_data('team_stats')

def load_batting_stats():
    return load_data('batting_stats')

def load_bowling_stats():
    return load_data('bowling_stats')

def load_match_data():
    return load_data('match_data')

def execute_query(query, params=()):
    """Execute a write query (INSERT, UPDATE, DELETE)."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        conn.close()
        return True, "Success"
    except Exception as e:
        return False, str(e)

def get_table_columns(table_name):
    """Get column names for a given table."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [row[1] for row in cursor.fetchall()]
        conn.close()
        return columns
    except Exception as e:
        print(f"Error getting columns for {table_name}: {e}")
        return []

def delete_record(table_name, id_column, id_value):
    """Delete a record from a table."""
    query = f"DELETE FROM {table_name} WHERE {id_column} = ?"
    return execute_query(query, (id_value,))

def update_record(table_name, id_column, id_value, data):
    """Update a record in a table."""
    cols = []
    vals = []
    for k, v in data.items():
        cols.append(f"{k} = ?")
        vals.append(v)
    
    vals.append(id_value)
    query = f"UPDATE {table_name} SET {', '.join(cols)} WHERE {id_column} = ?"
    return execute_query(query, tuple(vals))

def add_record(table_name, data):
    """Add a new record to a table."""
    cols = list(data.keys())
    placeholders = ['?' for _ in cols]
    vals = list(data.values())
    
    query = f"INSERT INTO {table_name} ({', '.join(cols)}) VALUES ({', '.join(placeholders)})"
    return execute_query(query, tuple(vals))
