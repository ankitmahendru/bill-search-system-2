import sqlite3
import random
import string
from werkzeug.security import generate_password_hash

DB_NAME = "bills.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # 1. ADMINS
    c.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')

    # 2. RESIDENTS (Updated: 'uid' is now the unique key for searching)
    c.execute('''
        CREATE TABLE IF NOT EXISTS residents (
            address TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            uid TEXT UNIQUE NOT NULL
        )
    ''')

    # 3. BILLS
    c.execute('''
        CREATE TABLE IF NOT EXISTS bills (
            bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
            address TEXT UNIQUE, 
            amount REAL,
            due_date TEXT,
            FOREIGN KEY(address) REFERENCES residents(address)
        )
    ''')

    # Master Admin
    try:
        pwhash = generate_password_hash("Master@2024")
        c.execute("INSERT INTO admins (username, password_hash) VALUES (?, ?)", 
                  ('master', pwhash))
        print("✅ Master Admin Created.")
    except sqlite3.IntegrityError:
        pass

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()