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
