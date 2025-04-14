import sqlite3
import os
from datetime import datetime

# Create database directory if it doesn't exist
os.makedirs('database', exist_ok=True)

def get_db_connection():
    """Creates a connection to the database."""
    return sqlite3.connect('database/history.db')

def init_db():
    """Initializes the database and creates tables."""
    conn = get_db_connection()
    c = conn.cursor()

    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id INTEGER PRIMARY KEY,
                 name TEXT,
                 budget_type TEXT,
                 family_id INTEGER)''')

    # Transactions table
    c.execute('''CREATE TABLE IF NOT EXISTS transactions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 user_id INTEGER, 
                 type TEXT, 
                 amount REAL, 
                 category TEXT,
                 description TEXT,
                 date TEXT)''')

    # Income categories table
    c.execute('''CREATE TABLE IF NOT EXISTS income_categories
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 user_id INTEGER,
                 name TEXT)''')

    # Expense categories table
    c.execute('''CREATE TABLE IF NOT EXISTS expense_categories
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 user_id INTEGER,
                 name TEXT)''')

    # Monthly statistics table
    c.execute('''CREATE TABLE IF NOT EXISTS monthly_stats
                 (user_id INTEGER,
                 year INTEGER,
                 month INTEGER,
                 total_income REAL,
                 total_expense REAL,
                 PRIMARY KEY (user_id, year, month))''')

    conn.commit()
    conn.close() 