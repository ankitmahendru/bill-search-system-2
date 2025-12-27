import sqlite3
from werkzeug.security import generate_password_hash

DB_NAME = "bills.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # 1. ADMINS TABLE (Kept simple)
    c.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')

    # 2. RESIDENTS TABLE (REQ 1: Address is Primary Key)
    # This stores permanent user data so you don't re-type names.
    c.execute('''
        CREATE TABLE IF NOT EXISTS residents (
            address TEXT PRIMARY KEY,
            name TEXT NOT NULL
        )
    ''')

    # 3. BILLS TABLE (REQ 3: Linked to Address)
    c.execute('''
        CREATE TABLE IF NOT EXISTS bills (
            bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
            address TEXT UNIQUE, 
            amount REAL,
            due_date TEXT,
            FOREIGN KEY(address) REFERENCES residents(address)
        )
    ''')

    # Create Default Master Admin
    try:
        # Change this password immediately after logging in!
        pwhash = generate_password_hash("Master@2024")
        c.execute("INSERT INTO admins (username, password_hash) VALUES (?, ?)", 
                  ('master', pwhash))
        print("✅ Master Admin Created: master / Master@2024")
    except sqlite3.IntegrityError:
        print("ℹ️ Admin already exists.")

    conn.commit()
    conn.close()
    print("✅ Database initialized successfully.")

if __name__ == "__main__":
    init_db()