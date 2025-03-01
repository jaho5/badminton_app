"""
Database connection and initialization module.
"""
import os
import sqlite3
import streamlit as st
from pathlib import Path

# Define the database path
DB_PATH = Path("badminton_app/data/puma.db")

def get_connection():
    """Create a connection to the SQLite database."""
    # Ensure data directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    # Connect to database
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

def init_db():
    """Initialize the database schema if it doesn't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        display_name TEXT,
        first_name TEXT,
        last_name TEXT
    )
    ''')
    
    # Create matches table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        side_1_user_1_id INTEGER NOT NULL,
        side_1_user_2_id INTEGER,
        side_2_user_1_id INTEGER NOT NULL,
        side_2_user_2_id INTEGER,
        set_1_side_1_score INTEGER,
        set_1_side_2_score INTEGER,
        set_2_side_1_score INTEGER,
        set_2_side_2_score INTEGER,
        set_3_side_1_score INTEGER,
        set_3_side_2_score INTEGER,
        on_court INTEGER,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create availables table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS availables (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL UNIQUE
    )
    ''')
    
    # Create elos table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS elos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        elo REAL NOT NULL
    )
    ''')
    
    # Create save table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS save (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL
    )
    ''')
    
    conn.commit()
    conn.close()

# Initialize the database in the Streamlit app
def setup_database():
    """Initialize the database when the Streamlit app starts."""
    # Use Streamlit's caching to ensure this only runs once per session
    if 'db_initialized' not in st.session_state:
        init_db()
        st.session_state.db_initialized = True
